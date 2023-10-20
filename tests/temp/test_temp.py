"""Temp test."""

from temp.temp import temp_false, temp_true


def test_temp_true() -> None:
    """Test temp_true."""
    assert temp_true() is True


def test_temp_false() -> None:
    """Test temp_false."""
    assert temp_false() is False
