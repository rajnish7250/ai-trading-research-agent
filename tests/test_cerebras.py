import os

import pytest


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_LLM_TESTS") != "1",
    reason="Live Cerebras API test is opt-in",
)
def test_cerebras_live_smoke():
    from agents.llm_provider import get_llm

    llm = get_llm("cerebras")
    response = llm.invoke(
        "Explain Bitcoin ETF inflows in 2 sentences."
    )

    assert response.content
