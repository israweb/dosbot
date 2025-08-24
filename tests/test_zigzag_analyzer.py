import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from zigzag_analyzer import ZigZagAnalyzer
    ZIGZAG_AVAILABLE = True
except ImportError:
    ZIGZAG_AVAILABLE = False


class TestZigZagAnalyzer:
    """Test cases for ZigZagAnalyzer class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        dates = pd.date_range('2023-01-01', periods=100, freq='15min')
        data = {
            'Open time': dates,
            'Open': np.random.uniform(40000, 50000, 100),
            'High': np.random.uniform(50000, 60000, 100),
            'Low': np.random.uniform(30000, 40000, 100),
            'Close': np.random.uniform(40000, 50000, 100),
            'zigzag (1.0%)': np.random.choice([-1, 0, 1], 100, p=[0.1, 0.8, 0.1])
        }
        return pd.DataFrame(data)
    
    @pytest.fixture
    def analyzer(self):
        """Create ZigZagAnalyzer instance."""
        if ZIGZAG_AVAILABLE:
            return ZigZagAnalyzer("test_data.csv")
        return None
    
    @pytest.mark.skipif(not ZIGZAG_AVAILABLE, reason="ZigZagAnalyzer module not available")
    def test_init(self, analyzer):
        """Test analyzer initialization."""
        assert analyzer.data_file == "test_data.csv"
        assert analyzer.data is None
        assert analyzer.zigzag_column is None
        assert analyzer.analysis_results == {}
    
    @pytest.mark.skipif(not ZIGZAG_AVAILABLE, reason="ZigZagAnalyzer module not available")
    @patch('pandas.read_csv')
    @patch('os.path.exists')
    def test_load_data_success(self, mock_exists, mock_read_csv, analyzer, sample_data):
        """Test successful data loading."""
        mock_exists.return_value = True
        mock_read_csv.return_value = sample_data
        
        result = analyzer.load_data()
        
        assert result is True
        assert analyzer.data is not None
        assert analyzer.zigzag_column == 'zigzag (1.0%)'
    
    @pytest.mark.skipif(not ZIGZAG_AVAILABLE, reason="ZigZagAnalyzer module not available")
    @patch('os.path.exists')
    def test_load_data_file_not_found(self, mock_exists, analyzer):
        """Test data loading when file doesn't exist."""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError):
            analyzer.load_data()
    
    @pytest.mark.skipif(not ZIGZAG_AVAILABLE, reason="ZigZagAnalyzer module not available")
    def test_analyze_zigzag_distances(self, analyzer, sample_data):
        """Test zigzag distance analysis."""
        analyzer.data = sample_data
        analyzer.zigzag_column = 'zigzag (1.0%)'
        
        result = analyzer.analyze_zigzag_distances()
        
        assert result is True
        assert 'total_points' in analyzer.analysis_results
        assert 'price_distances' in analyzer.analysis_results
        assert 'percent_distances' in analyzer.analysis_results
    
    @pytest.mark.skipif(not ZIGZAG_AVAILABLE, reason="ZigZagAnalyzer module not available")
    def test_calculate_statistics(self, analyzer, sample_data):
        """Test statistics calculation."""
        analyzer.data = sample_data
        analyzer.zigzag_column = 'zigzag (1.0%)'
        analyzer.analyze_zigzag_distances()
        
        stats = analyzer.calculate_statistics()
        
        assert stats is not False
        assert 'Метрика' in stats
        assert len(stats['Метрика']) == 3
    
    @pytest.mark.skipif(not ZIGZAG_AVAILABLE, reason="ZigZagAnalyzer module not available")
    def test_check_minimum_distances(self, analyzer, sample_data):
        """Test minimum distance checking."""
        analyzer.data = sample_data
        analyzer.zigzag_column = 'zigzag (1.0%)'
        analyzer.analyze_zigzag_distances()
        
        result = analyzer.check_minimum_distances(1.0)
        
        assert isinstance(result, bool)
