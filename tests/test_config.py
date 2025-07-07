"""
Tests for the configuration module.
"""
import pytest
from pathlib import Path

from src.config import (
    LORE_TO_WIN,
    STARTING_HAND_SIZE,
    MAX_DECK_SIZE,
    DATA_DIR,
    CARDS_DATABASE_PATH,
    COMMUNITY_CARDS_URL,
    DECK_ANALYSIS_CSV,
    GAME_STATISTICS_CSV,
    CARD_USAGE_CSV,
)


def test_game_constants_exist():
    """Test that game-related constants exist and have correct types."""
    assert isinstance(LORE_TO_WIN, int)
    assert isinstance(STARTING_HAND_SIZE, int)
    assert isinstance(MAX_DECK_SIZE, int)


def test_game_constants_values():
    """Test that game-related constants have reasonable values."""
    assert LORE_TO_WIN > 0
    assert STARTING_HAND_SIZE > 0
    assert MAX_DECK_SIZE > 0
    assert STARTING_HAND_SIZE < MAX_DECK_SIZE


def test_path_constants_exist():
    """Test that path constants exist and have correct types."""
    assert isinstance(DATA_DIR, Path)
    assert isinstance(CARDS_DATABASE_PATH, Path)


def test_path_constants_values():
    """Test that path constants point to valid locations."""
    assert DATA_DIR.exists(), "Data directory does not exist"
    # Note: CARDS_DATABASE_PATH might not exist yet if no data has been downloaded


def test_url_constants_exist():
    """Test that URL constants exist and have correct types."""
    assert isinstance(COMMUNITY_CARDS_URL, str)
    assert COMMUNITY_CARDS_URL.startswith("http")


def test_output_file_constants_exist():
    """Test that output file name constants exist and have correct types."""
    assert isinstance(DECK_ANALYSIS_CSV, str)
    assert isinstance(GAME_STATISTICS_CSV, str)
    assert isinstance(CARD_USAGE_CSV, str)


def test_output_file_constants_values():
    """Test that output file name constants have correct extensions."""
    assert DECK_ANALYSIS_CSV.endswith(".csv")
    assert GAME_STATISTICS_CSV.endswith(".csv")
    assert CARD_USAGE_CSV.endswith(".csv")
