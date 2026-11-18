#!/usr/bin/env bash
set -Eeuo pipefail

# Usage: deploy-production.sh <40-character-commit-sha> <s3-bucket>
# Artifacts are stored under deployments/<commit-sha>/ in the bucket.

if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <commit-sha> <s3-bucket>" >&2
  exit 2
fi

DEPLOYMENT_SHA="$1"
S3_BUCKET="$2"

if [[ ! "$DEPLOYMENT_SHA" =~ ^[0-9a-f]{40}$ ]]; then
  echo "ERROR: Invalid commit SHA." >&2
  exit 2
fi

API_REPO="rajnishk2439/ai-trading-api"
FRONTEND_REPO="rajnishk2439/ai-trading-frontend"
IMAGE_TAG="$DEPLOYMENT_SHA"
FRONTEND_IMAGE_TAG="$DEPLOYMENT_SHA"
IMAGE="${API_REPO}:${IMAGE_TAG}"
FRONTEND_IMAGE="${FRONTEND_REPO}:${FRONTEND_IMAGE_TAG}"

APP_DIR="/home/ubuntu/ai-trading-research-agent"
COMPOSE_FILE="${APP_DIR}/docker-compose.prod.yml"
COMPOSE_CANDIDATE="${APP_DIR}/docker-compose.prod.yml.candidate"
COMPOSE_BACKUP="${APP_DIR}/docker-compose.prod.yml.previous"
UPLOADED_COMPOSE="/tmp/docker-compose.prod.yml.${DEPLOYMENT_SHA}"
ENV_FILE="${APP_DIR}/.env"
DATA_DIR="/home/ubuntu/trading-api-data"
ARTIFACT_PREFIX="s3://${S3_BUCKET}/deployments/${DEPLOYMENT_SHA}"

echo "======================================"
echo "AI Trading Research Agent deployment"
echo "Commit: ${DEPLOYMENT_SHA}"
echo "API: ${IMAGE}"
echo "Frontend: ${FRONTEND_IMAGE}"
echo "======================================"

# 1. Validate host prerequisites before changing production.
if [[ ! -d "$APP_DIR" ]]; then
  echo "ERROR: Application directory not found: $APP_DIR"
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "ERROR: Environment file not found."
  exit 1
fi
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "ERROR: Active production Compose file not found."
  exit 1
fi
if [[ ! -d "$DATA_DIR/chroma_db" ]]; then
  echo "ERROR: ChromaDB directory not found."
  exit 1
fi
if [[ ! -f "$DATA_DIR/research_history.db" ]]; then
  echo "ERROR: Research history database not found."
  exit 1
fi
docker compose version >/dev/null
command -v aws >/dev/null
command -v curl >/dev/null

AVAILABLE_BYTES="$(df -PB1 / | awk 'NR==2 {print $4}')"
MIN_FREE_BYTES=$((15 * 1024 * 1024 * 1024))
echo "Available disk space: ${AVAILABLE_BYTES} bytes"
if (( AVAILABLE_BYTES < MIN_FREE_BYTES )); then
  echo "ERROR: At least 15 GiB free disk space is required."
  exit 1
fi

# 2. Fetch the Compose candidate for this exact commit.
rm -f "$UPLOADED_COMPOSE"
aws s3 cp "${ARTIFACT_PREFIX}/docker-compose.prod.yml" "$UPLOADED_COMPOSE" --only-show-errors
if [[ ! -s "$UPLOADED_COMPOSE" ]]; then
  echo "ERROR: S3 Compose artifact is missing or empty."
  exit 1
fi
cp "$UPLOADED_COMPOSE" "$COMPOSE_CANDIDATE"

cd "$APP_DIR"
export IMAGE IMAGE_TAG FRONTEND_IMAGE FRONTEND_IMAGE_TAG

# 3. Validate candidate and pull both images before touching running services.
echo "Validating candidate Compose configuration..."
docker compose -f "$COMPOSE_CANDIDATE" config --quiet

echo "Pulling exact API image: $IMAGE"
docker pull "$IMAGE"
echo "Pulling exact frontend image: $FRONTEND_IMAGE"
docker pull "$FRONTEND_IMAGE"

NEW_API_IMAGE_ID="$(docker image inspect --format '{{.Id}}' "$IMAGE")"
NEW_FRONTEND_IMAGE_ID="$(docker image inspect --format '{{.Id}}' "$FRONTEND_IMAGE")"

# 4. Health-check helpers.
wait_for_api_health() {
  local attempt=1
  echo "Checking FastAPI health..."
  while (( attempt <= 30 )); do
    if curl --silent --show-error --fail http://127.0.0.1:8000/health >/dev/null; then
      echo "FastAPI is healthy."
      return 0
    fi
    echo "Waiting for FastAPI... (${attempt}/30)"
    sleep 5
    attempt=$((attempt + 1))
  done
  echo "ERROR: FastAPI health check failed."
  return 1
}

wait_for_frontend_health() {
  local attempt=1
  echo "Checking Streamlit health..."
  while (( attempt <= 30 )); do
    if curl --silent --show-error --fail http://127.0.0.1:8501/_stcore/health >/dev/null; then
      echo "Streamlit is healthy."
      return 0
    fi
    echo "Waiting for Streamlit... (${attempt}/30)"
    sleep 5
    attempt=$((attempt + 1))
  done
  echo "ERROR: Streamlit health check failed."
  return 1
}

wait_for_all_health() {
  wait_for_api_health && wait_for_frontend_health
}

EXPECTED_COMPOSE_PROJECT="$(basename "$APP_DIR")"

is_expected_compose_container() {
  local container="$1"
  local expected_service="$2"
  local actual_project
  local actual_service

  if ! docker inspect "$container" >/dev/null 2>&1; then
    echo "Container $container does not exist."
    return 1
  fi

  actual_project="$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project" }}' "$container")"
  actual_service="$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.service" }}' "$container")"

  [[ "$actual_project" == "$EXPECTED_COMPOSE_PROJECT" &&
     "$actual_service" == "$expected_service" ]]
}

assert_container_is_expected_or_absent() {
  local container="$1"
  local expected_service="$2"

  if ! docker inspect "$container" >/dev/null 2>&1; then
    echo "Container $container is absent. Nothing to validate."
    return 0
  fi

  if ! is_expected_compose_container "$container" "$expected_service"; then
    echo "CRITICAL: Container $container does not belong to the expected Compose project/service." >&2
    return 1
  fi

  echo "Verified container identity: $container ($expected_service)"
}

remove_expected_compose_container() {
  local container="$1"
  local expected_service="$2"

  if ! docker inspect "$container" >/dev/null 2>&1; then
    echo "Container $container is already absent."
    return 0
  fi

  if ! is_expected_compose_container "$container" "$expected_service"; then
    echo "CRITICAL: Refusing to remove unverified container: $container" >&2
    return 1
  fi

  echo "Removing verified Compose container: $container"
  docker rm -f "$container"
}

# 5. Capture the currently running versions.
OLD_CONTAINER=""
PREVIOUS_API_IMAGE=""
PREVIOUS_API_IMAGE_ID=""
PREVIOUS_FRONTEND_IMAGE=""
PREVIOUS_FRONTEND_IMAGE_ID=""
BACKUP_CONTAINER=""

if docker inspect trading-api >/dev/null 2>&1; then
  OLD_CONTAINER="trading-api"
  PREVIOUS_API_IMAGE="$(docker inspect --format '{{.Config.Image}}' "$OLD_CONTAINER")"
  PREVIOUS_API_IMAGE_ID="$(docker inspect --format '{{.Image}}' "$OLD_CONTAINER")"
  echo "Previous API image: $PREVIOUS_API_IMAGE"
else
  echo "WARNING: No existing API container identified."
fi

if docker inspect trading-frontend >/dev/null 2>&1; then
  PREVIOUS_FRONTEND_IMAGE="$(docker inspect --format '{{.Config.Image}}' trading-frontend)"
  PREVIOUS_FRONTEND_IMAGE_ID="$(docker inspect --format '{{.Image}}' trading-frontend)"
  echo "Previous frontend image: $PREVIOUS_FRONTEND_IMAGE"
else
  echo "No previous frontend container found."
fi

# 6. Back up the active Compose file before any container migration.
echo "Backing up active production Compose configuration..."
cp -p "$COMPOSE_FILE" "$COMPOSE_BACKUP"

# 7. Detect Docker Run -> Compose migration and preserve the old API container.
IS_COMPOSE_MANAGED=0
if [[ -n "$OLD_CONTAINER" ]]; then
  COMPOSE_PROJECT="$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project" }}' "$OLD_CONTAINER")"
  if [[ "$COMPOSE_PROJECT" != "<no value>" && -n "$COMPOSE_PROJECT" ]]; then
    IS_COMPOSE_MANAGED=1
  fi
fi

restore_predeployment_migration() {
  local failed=0

  if [[ -n "$BACKUP_CONTAINER" ]] && docker inspect "$BACKUP_CONTAINER" >/dev/null 2>&1; then
    echo "PRE-DEPLOYMENT RECOVERY: Restoring original Docker Run API container..."
    if docker inspect trading-api >/dev/null 2>&1; then
      echo "WARNING: trading-api name is occupied; not removing an unverified container."
      failed=1
    else
      docker rename "$BACKUP_CONTAINER" trading-api || failed=1
      if [[ "$failed" -eq 0 ]]; then
        docker start trading-api || failed=1
      fi
    fi
  fi

  if [[ -f "$COMPOSE_BACKUP" ]]; then
    local restore_file="${COMPOSE_FILE}.predeploy-restore"
    if cp -p "$COMPOSE_BACKUP" "$restore_file" && mv -f "$restore_file" "$COMPOSE_FILE"; then
      echo "Restored active Compose configuration after interrupted preparation."
    else
      echo "CRITICAL: Could not restore previous Compose configuration."
      failed=1
    fi
  fi

  if [[ "$failed" -eq 0 ]]; then
    echo "Pre-deployment recovery completed."
  else
    echo "CRITICAL: Pre-deployment recovery was incomplete. Manual inspection is required."
  fi
  return "$failed"
}

predeployment_exit_handler() {
  local exit_status="$?"
  trap - EXIT

  if [[ "$PREDEPLOY_MIGRATION_ACTIVE" -eq 1 ]]; then
    echo "Unexpected exit during migration preparation (status ${exit_status})."

    if ! restore_predeployment_migration; then
      echo "CRITICAL: Pre-deployment recovery failed. Manual inspection is required." >&2
      exit 1
    fi
  fi

  exit "$exit_status"
}

# Keep recovery active through preparation. It is disabled only immediately
# before Compose starts, when the explicit deployment rollback takes over.
PREDEPLOY_MIGRATION_ACTIVE=1
trap predeployment_exit_handler EXIT

if [[ -n "$OLD_CONTAINER" && "$IS_COMPOSE_MANAGED" -eq 0 ]]; then
  BACKUP_CONTAINER="trading-api-previous-$(date +%Y%m%d%H%M%S)"
  echo "First migration detected; preserving existing Docker Run container."
  if ! docker stop "$OLD_CONTAINER"; then
    echo "ERROR: Could not stop existing API container."
    exit 1
  fi
  if ! docker rename "$OLD_CONTAINER" "$BACKUP_CONTAINER"; then
    echo "ERROR: Could not preserve existing API container."
    docker start "$OLD_CONTAINER" || true
    PREDEPLOY_MIGRATION_ACTIVE=0
    exit 1
  fi
fi

# 8. Atomically activate the validated candidate. The EXIT handler protects
# preparation until the normal deployment rollback path takes over.
if ! mv -f "$COMPOSE_CANDIDATE" "$COMPOSE_FILE"; then
  echo "ERROR: Could not activate candidate Compose configuration."
  exit 1
fi

# 8. Rollback restores previous Compose config and service images.
rollback_deployment() {
  echo "======================================"
  echo "ROLLBACK STARTED"
  echo "======================================"

  if [[ ! -f "$COMPOSE_BACKUP" ]]; then
    echo "CRITICAL: Previous Compose backup is missing."
    return 1
  fi
  local restore_file="${COMPOSE_FILE}.restore"
  cp -p "$COMPOSE_BACKUP" "$restore_file" || return 1
  mv -f "$restore_file" "$COMPOSE_FILE" || return 1

  if [[ -n "$BACKUP_CONTAINER" ]]; then
    echo "Restoring original Docker Run API container..."

    # Validate both containers before removing either one.
    assert_container_is_expected_or_absent trading-frontend trading-frontend || return 1
    assert_container_is_expected_or_absent trading-api trading-api || return 1

    # Remove only containers belonging to our expected Compose project.
    remove_expected_compose_container trading-frontend trading-frontend || return 1
    remove_expected_compose_container trading-api trading-api || return 1

    docker rename "$BACKUP_CONTAINER" trading-api || return 1
    docker start trading-api || return 1
    wait_for_api_health || return 1
    return 0
  fi

  if [[ -n "$PREVIOUS_API_IMAGE" ]]; then
    if ! docker image inspect "$PREVIOUS_API_IMAGE" >/dev/null 2>&1; then
      docker tag "$PREVIOUS_API_IMAGE_ID" "$PREVIOUS_API_IMAGE" || return 1
    fi
    IMAGE="$PREVIOUS_API_IMAGE"
    IMAGE_TAG="${PREVIOUS_API_IMAGE##*:}"
    export IMAGE IMAGE_TAG

    if [[ -n "$PREVIOUS_FRONTEND_IMAGE" ]]; then
      if ! docker image inspect "$PREVIOUS_FRONTEND_IMAGE" >/dev/null 2>&1; then
        docker tag "$PREVIOUS_FRONTEND_IMAGE_ID" "$PREVIOUS_FRONTEND_IMAGE" || return 1
      fi
      FRONTEND_IMAGE="$PREVIOUS_FRONTEND_IMAGE"
      FRONTEND_IMAGE_TAG="${PREVIOUS_FRONTEND_IMAGE##*:}"
      export FRONTEND_IMAGE FRONTEND_IMAGE_TAG
      echo "Restoring previous API and frontend images..."
      docker compose -f "$COMPOSE_FILE" up -d --no-build --force-recreate || return 1
      wait_for_all_health || return 1
    else
      echo "Restoring previous API; removing first-time frontend deployment..."
      docker compose -f "$COMPOSE_FILE" up -d --no-build --no-deps --force-recreate trading-api || return 1
      docker rm -f trading-frontend || true
      wait_for_api_health || return 1
    fi
    echo "Previous production version restored."
    return 0
  fi

  echo "No previous API version available."
  docker rm -f trading-frontend || true
  docker rm -f trading-api || true
  return 0
}

# 9. Deploy and roll back on Compose failure or failed health checks.
# From this point, the explicit rollback function owns recovery.
PREDEPLOY_MIGRATION_ACTIVE=0
trap - EXIT
echo "Starting API and frontend using Docker Compose..."
if ! docker compose -f "$COMPOSE_FILE" up -d --no-build --force-recreate; then
  echo "ERROR: Docker Compose deployment failed."
  if ! rollback_deployment; then
    echo "CRITICAL: Rollback failed."
    docker logs --tail 100 trading-api || true
    docker logs --tail 100 trading-frontend || true
    exit 1
  fi
  echo "Deployment failed. Previous state restored."
  exit 1
fi

echo "Waiting for both applications to become healthy..."
if ! wait_for_all_health; then
  echo "ERROR: One or more applications failed health checks."
  docker logs --tail 100 trading-api || true
  docker logs --tail 100 trading-frontend || true
  if ! rollback_deployment; then
    echo "CRITICAL: Rollback failed."
    docker logs --tail 100 trading-api || true
    docker logs --tail 100 trading-frontend || true
    exit 1
  fi
  echo "Deployment failed. Previous state restored."
  exit 1
fi

echo "Both applications are healthy."

# 10. Remove old Docker Run container only after successful health checks.
if [[ -n "$BACKUP_CONTAINER" ]]; then
  echo "Removing previous Docker Run container..."
  docker rm "$BACKUP_CONTAINER" || echo "WARNING: Could not remove previous backup container."
fi

# 11. Retain current and previous image IDs; remove other tagged repo images.
cleanup_repo_images() {
  local repository="$1"
  local current_id="$2"
  local previous_id="$3"
  echo "Cleaning obsolete images from ${repository}..."
  docker image ls --no-trunc -q "$repository" | sort -u |
  while IFS= read -r image_id; do
    if [[ -n "$image_id" && "$image_id" != "$current_id" && "$image_id" != "$previous_id" ]]; then
      echo "Removing obsolete image: $image_id"
      docker rmi "$image_id" || echo "WARNING: Could not remove $image_id"
    fi
  done
}

cleanup_repo_images "$API_REPO" "$NEW_API_IMAGE_ID" "$PREVIOUS_API_IMAGE_ID"
cleanup_repo_images "$FRONTEND_REPO" "$NEW_FRONTEND_IMAGE_ID" "$PREVIOUS_FRONTEND_IMAGE_ID"

rm -f "$UPLOADED_COMPOSE"
echo "======================================"
echo "Deployment completed successfully."
echo "API image: $IMAGE"
echo "Frontend image: $FRONTEND_IMAGE"
echo "======================================"
