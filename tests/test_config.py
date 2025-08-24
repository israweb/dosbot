import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from config import API_KEY, API_SECRET, BASE_URL, MODEL_PARAMS, TRADING_SETTINGS, Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Config module not available")
def test_config_constants():
    """Test that configuration constants are defined."""
    assert API_KEY is not None
    assert API_SECRET is not None
    assert BASE_URL is not None
    assert isinstance(BASE_URL, str)


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Config module not available")
def test_model_parameters():
    """Test model parameters are properly set."""
    assert isinstance(MODEL_PARAMS, dict)
    assert "learning_rate" in MODEL_PARAMS
    assert "epochs" in MODEL_PARAMS
    assert "batch_size" in MODEL_PARAMS
    assert isinstance(MODEL_PARAMS["learning_rate"], float)
    assert MODEL_PARAMS["learning_rate"] > 0


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Config module not available")
def test_trading_settings():
    """Test trading configuration."""
    assert isinstance(TRADING_SETTINGS, dict)
    assert "trade_amount" in TRADING_SETTINGS
    assert "stop_loss" in TRADING_SETTINGS
    assert "take_profit" in TRADING_SETTINGS
    assert isinstance(TRADING_SETTINGS["trade_amount"], (int, float))
    assert TRADING_SETTINGS["trade_amount"] > 0


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Config module not available")
def test_config_class():
    """Test Config class initialization."""
    config = Config()
    assert config.symbol == "BTCUSDT"
    assert config.timeframe == "1h"
    assert config.max_retries == 3
    assert config.log_level == "INFO"
    assert config.trade_interval == 60
