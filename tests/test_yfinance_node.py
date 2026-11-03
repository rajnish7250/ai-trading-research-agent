
from unittest.mock import MagicMock, patch

import pytest

from nodes.yfinance_node import yfinance_mode


@pytest.fixture
def state():
    return {
        "messages": [
            MagicMock(content="What is the current price of Bitcoin?")
        ]
    }


@patch("nodes.yfinance_node.detect_symbol", return_value="BTC-USD")
@patch("nodes.yfinance_node.get_crypto_price")
def test_yfinance_node_fetches_crypto_price(
    mock_crypto,
    mock_detect_symbol,
    state,
):
    mock_crypto.invoke.return_value = {"price": 80000}

    result = yfinance_mode(state)

    assert result["market_price_data"] == "{'price': 80000}"
    mock_crypto.invoke.assert_called_once_with("BTC-USD")


@patch("nodes.yfinance_node.detect_symbol", return_value="AAPL")
@patch("nodes.yfinance_node.get_stock_price")
def test_yfinance_node_fetches_stock_price(
    mock_stock,
    mock_detect_symbol,
    state,
):
    mock_stock.invoke.return_value = {"price": 250}

    result = yfinance_mode(state)

    assert result["market_price_data"] == "{'price': 250}"
    mock_stock.invoke.assert_called_once_with("AAPL")


@patch("nodes.yfinance_node.detect_symbol", return_value=None)
def test_yfinance_node_handles_unsupported_asset(
    mock_detect_symbol,
    state,
):
    result = yfinance_mode(state)

    assert result["market_price_data"] == (
        "No supported asset detected."
    )


@patch("nodes.yfinance_node.detect_symbol", return_value="BTC-USD")
@patch("nodes.yfinance_node.get_crypto_price")
def test_yfinance_node_reraises_price_fetch_exception(
    mock_crypto,
    mock_detect_symbol,
    state,
):
    mock_crypto.invoke.side_effect = RuntimeError(
        "Price service unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="Price service unavailable",
    ):
        yfinance_mode(state)
