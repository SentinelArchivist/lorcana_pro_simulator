"""
Tests for the CardDatabase class.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from requests.exceptions import RequestException

from src.card_database import CardDatabase
from src.config import CARDS_DATABASE_PATH, DATA_DIR


@pytest.fixture
def sample_card_data():
    """Sample card data for testing."""
    return [
        {
            "name": "Mickey Mouse - Brave Little Tailor",
            "cost": 3,
            "inkable": True,
            "color": "Amber",
            "type": "Character",
            "subtypes": ["Hero"],
            "attack": 2,
            "defense": 3,
            "lore": 1,
            "abilities": ["When this character quests, gain 1 lore."]
        },
        {
            "name": "Maleficent - Mistress of Evil",
            "cost": 6,
            "inkable": True,
            "color": "Amethyst",
            "type": "Character",
            "subtypes": ["Villain", "Sorcerer"],
            "attack": 5,
            "defense": 5,
            "lore": 2,
            "abilities": ["When this character enters play, deal 2 damage to target character."]
        }
    ]


@pytest.fixture
def setup_test_data(tmp_path, monkeypatch, sample_card_data):
    """Setup test environment with temporary directories and mock data."""
    # Create a temporary data directory
    test_data_dir = tmp_path / "data"
    test_data_dir.mkdir()
    test_cards_path = test_data_dir / "cards.json"
    
    # Patch the config paths to use our test paths
    monkeypatch.setattr("src.card_database.DATA_DIR", test_data_dir)
    monkeypatch.setattr("src.card_database.CARDS_DATABASE_PATH", test_cards_path)
    
    return {
        "data_dir": test_data_dir,
        "cards_path": test_cards_path,
        "sample_data": sample_card_data
    }


def test_init_with_existing_file(setup_test_data):
    """Test initialization when cards.json already exists."""
    # Arrange
    test_env = setup_test_data
    
    # Create a cards.json file with sample data
    with open(test_env["cards_path"], 'w', encoding='utf-8') as f:
        json.dump(test_env["sample_data"], f)
    
    # Act
    db = CardDatabase()
    
    # Assert
    assert len(db.cards) == 2
    assert "Mickey Mouse - Brave Little Tailor" in db.cards
    assert "Maleficent - Mistress of Evil" in db.cards


def test_download_cards_success(setup_test_data, monkeypatch):
    """Test successful download of cards when file doesn't exist."""
    # Arrange
    test_env = setup_test_data
    
    # Mock the requests.get function
    mock_response = MagicMock()
    mock_response.text = json.dumps(test_env["sample_data"])
    mock_response.json = MagicMock(return_value=test_env["sample_data"])
    mock_response.raise_for_status = MagicMock()
    
    mock_get = MagicMock(return_value=mock_response)
    monkeypatch.setattr("src.card_database.requests.get", mock_get)
    
    # Act
    db = CardDatabase()
    
    # Assert
    mock_get.assert_called_once()
    assert test_env["cards_path"].exists()
    assert len(db.cards) == 2
    assert "Mickey Mouse - Brave Little Tailor" in db.cards


def test_download_cards_failure(setup_test_data, monkeypatch):
    """Test handling of download failure."""
    # Arrange
    test_env = setup_test_data
    
    # Mock the requests.get function to raise an exception
    mock_get = MagicMock(side_effect=RequestException("Network error"))
    monkeypatch.setattr("src.card_database.requests.get", mock_get)
    
    # Act & Assert
    with pytest.raises(RuntimeError) as excinfo:
        CardDatabase()
    
    assert "Could not initialize card database" in str(excinfo.value)
    mock_get.assert_called_once()


def test_load_cards_with_corrupted_json(setup_test_data):
    """Test handling of corrupted JSON file."""
    # Arrange
    test_env = setup_test_data
    
    # Create a corrupted JSON file
    with open(test_env["cards_path"], 'w', encoding='utf-8') as f:
        f.write("This is not valid JSON")
    
    # Act & Assert
    with pytest.raises(RuntimeError) as excinfo:
        CardDatabase()
    
    assert "Card data file is corrupted" in str(excinfo.value)


def test_get_card_success(setup_test_data):
    """Test successful retrieval of a card."""
    # Arrange
    test_env = setup_test_data
    
    # Create a cards.json file with sample data
    with open(test_env["cards_path"], 'w', encoding='utf-8') as f:
        json.dump(test_env["sample_data"], f)
    
    # Act
    db = CardDatabase()
    card = db.get_card("Mickey Mouse - Brave Little Tailor")
    
    # Assert
    assert card is not None
    assert card["name"] == "Mickey Mouse - Brave Little Tailor"
    assert card["cost"] == 3
    assert card["color"] == "Amber"


def test_get_card_not_found(setup_test_data):
    """Test retrieval of a non-existent card."""
    # Arrange
    test_env = setup_test_data
    
    # Create a cards.json file with sample data
    with open(test_env["cards_path"], 'w', encoding='utf-8') as f:
        json.dump(test_env["sample_data"], f)
    
    # Act
    db = CardDatabase()
    card = db.get_card("Non-existent Card")
    
    # Assert
    assert card is None
