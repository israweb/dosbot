"""Basic tests to verify test environment is working."""

def test_basic_math():
    """Test basic math operations."""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5


def test_basic_string():
    """Test basic string operations."""
    assert "hello" + " world" == "hello world"
    assert "test".upper() == "TEST"


def test_basic_list():
    """Test basic list operations."""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1
