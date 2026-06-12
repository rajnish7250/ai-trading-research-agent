from nodes.memory_filter_node import (
    memory_filter_node
)

mock_state = {
    "research_summary":
    """
    NEWS:
    ETF inflows increased this week.

    SENTIMENT:
    Positive

    RISK:
    Low Risk
    """
}

result = memory_filter_node(
    mock_state
)

print(result)