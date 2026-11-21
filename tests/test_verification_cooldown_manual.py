import sqlite3
import tempfile
import unittest

from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import auth.user_repository as users
import auth.token_repository as tokens


class VerificationCooldownTest(unittest.TestCase):

    def test_verification_cooldown(self):

        # Step 1: Create a temporary test database.
        with tempfile.TemporaryDirectory() as folder:

            test_db = Path(folder) / "test_auth.db"

            with (
                patch.object(users, "DB_PATH", test_db),
                patch.object(tokens, "DB_PATH", test_db),
            ):

                users.init_users_db()
                tokens.init_auth_tokens_db()

                # Step 2: Create a fake unverified user.
                user_id = users.create_user(
                    email="student@example.com",
                    full_name="Test Student",
                    hashed_password="FAKE_HASH",
                )

                expiry = (
                    datetime.now(timezone.utc)
                    + timedelta(minutes=30)
                ).isoformat()

                # Step 3: First request should succeed.
                first = tokens.save_verification_token_with_cooldown(
                    user_id=user_id,
                    token_hash="fake-hash-1",
                    expires_at=expiry,
                )

                self.assertTrue(first)

                # Step 4: Immediate second request should fail.
                second = tokens.save_verification_token_with_cooldown(
                    user_id=user_id,
                    token_hash="fake-hash-2",
                    expires_at=expiry,
                )

                self.assertFalse(second)

                # Step 5: Only one token should be saved.
                with closing(sqlite3.connect(test_db)) as connection:
                    count = connection.execute(
                        """
                        SELECT COUNT(*)
                        FROM auth_tokens
                        WHERE user_id = ?
                        """,
                        (user_id,),
                    ).fetchone()[0]

                self.assertEqual(count, 1)

                # Step 6: Create two more fake users.
                verified_id = users.create_user(
                    email="verified@example.com",
                    full_name="Verified Student",
                    hashed_password="FAKE_HASH",
                )

                disabled_id = users.create_user(
                    email="disabled@example.com",
                    full_name="Disabled Student",
                    hashed_password="FAKE_HASH",
                )

                # Step 7: Update their account statuses.
                with closing(sqlite3.connect(test_db)) as connection:
                    connection.execute(
                        "UPDATE users SET is_verified = 1 WHERE id = ?",
                        (verified_id,),
                    )

                    connection.execute(
                        "UPDATE users SET disabled = 1 WHERE id = ?",
                        (disabled_id,),
                    )

                    connection.commit()

                # Step 8: Verified users should be blocked.
                self.assertFalse(
                    tokens.save_verification_token_with_cooldown(
                        user_id=verified_id,
                        token_hash="fake-hash-3",
                        expires_at=expiry,
                    )
                )

                # Step 9: Disabled users should be blocked.
                self.assertFalse(
                    tokens.save_verification_token_with_cooldown(
                        user_id=disabled_id,
                        token_hash="fake-hash-4",
                        expires_at=expiry,
                    )
                )


if __name__ == "__main__":
    unittest.main()