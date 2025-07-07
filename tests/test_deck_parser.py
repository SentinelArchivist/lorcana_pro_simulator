"""
Tests for the Deck Parser module.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from src.deck_parser import parse_decklist
from src.card_database import CardDatabase


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
        },
        {
            "name": "Stitch - Rock Star",
            "cost": 4,
            "inkable": True,
            "color": "Ruby",
            "type": "Character",
            "subtypes": ["Alien"],
            "attack": 3,
            "defense": 4,
            "lore": 1,
            "abilities": ["When this character enters play, exert target character."]
        },
        {
            "name": "Elsa - Snow Queen",
            "cost": 5,
            "inkable": True,
            "color": "Sapphire",
            "type": "Character",
            "subtypes": ["Queen", "Sorcerer"],
            "attack": 4,
            "defense": 4,
            "lore": 2,
            "abilities": ["When this character enters play, freeze target character."]
        },
        {
            "name": "Magical Surge",
            "cost": 2,
            "inkable": False,
            "color": "Amethyst",
            "type": "Action",
            "subtypes": ["Spell"],
            "attack": None,
            "defense": None,
            "lore": None,
            "abilities": ["Deal 2 damage to target character."]
        }
    ]


@pytest.fixture
def mock_card_db(sample_card_data):
    """Create a mock CardDatabase for testing."""
    mock_db = MagicMock(spec=CardDatabase)
    
    # Set up the get_card method to return cards from our sample data
    def mock_get_card(name):
        for card in sample_card_data:
            if card["name"] == name:
                return card
        return None
    
    mock_db.get_card = mock_get_card
    return mock_db


@pytest.fixture
def setup_test_files(tmp_path):
    """Create test decklist files."""
    test_dir = tmp_path / "decklists"
    test_dir.mkdir()
    
    # Valid decklist file with 60 cards
    valid_file = test_dir / "valid_decklist.md"
    with open(valid_file, 'w', encoding='utf-8') as f:
        f.write("[Test Deck 1]\n")
        f.write("20 Mickey Mouse - Brave Little Tailor\n")
        f.write("20 Maleficent - Mistress of Evil\n")
        f.write("20 Stitch - Rock Star\n")
        f.write("\n")
        f.write("[Test Deck 2]\n")
        f.write("15 Mickey Mouse - Brave Little Tailor\n")
        f.write("15 Maleficent - Mistress of Evil\n")
        f.write("15 Stitch - Rock Star\n")
        f.write("15 Elsa - Snow Queen\n")
    
    # Invalid decklist with a bad card name
    bad_card_file = test_dir / "bad_card_decklist.md"
    with open(bad_card_file, 'w', encoding='utf-8') as f:
        f.write("[Bad Card Deck]\n")
        f.write("30 Mickey Mouse - Brave Little Tailor\n")
        f.write("30 Non-existent Card\n")
    
    # Invalid decklist with incorrect card count (59 cards)
    bad_count_file = test_dir / "bad_count_decklist.md"
    with open(bad_count_file, 'w', encoding='utf-8') as f:
        f.write("[Bad Count Deck]\n")
        f.write("20 Mickey Mouse - Brave Little Tailor\n")
        f.write("20 Maleficent - Mistress of Evil\n")
        f.write("19 Stitch - Rock Star\n")
    
    return {
        "test_dir": test_dir,
        "valid_file": valid_file,
        "bad_card_file": bad_card_file,
        "bad_count_file": bad_count_file,
        "missing_file": test_dir / "nonexistent_file.md"
    }


def test_parse_valid_decklist(setup_test_files, mock_card_db):
    """Test parsing a valid decklist file."""
    # Arrange
    test_files = setup_test_files
    
    # Act
    decks = parse_decklist(str(test_files["valid_file"]), mock_card_db)
    
    # Assert
    assert len(decks) == 2
    
    # Check first deck
    assert decks[0]["name"] == "Test Deck 1"
    assert len(decks[0]["cards"]) == 60
    
    # Count cards in first deck
    card_counts = {}
    for card in decks[0]["cards"]:
        card_name = card["name"]
        card_counts[card_name] = card_counts.get(card_name, 0) + 1
    
    assert card_counts["Mickey Mouse - Brave Little Tailor"] == 20
    assert card_counts["Maleficent - Mistress of Evil"] == 20
    assert card_counts["Stitch - Rock Star"] == 20
    
    # Check second deck
    assert decks[1]["name"] == "Test Deck 2"
    assert len(decks[1]["cards"]) == 60
    
    # Count cards in second deck
    card_counts = {}
    for card in decks[1]["cards"]:
        card_name = card["name"]
        card_counts[card_name] = card_counts.get(card_name, 0) + 1
    
    assert card_counts["Mickey Mouse - Brave Little Tailor"] == 15
    assert card_counts["Maleficent - Mistress of Evil"] == 15
    assert card_counts["Stitch - Rock Star"] == 15
    assert card_counts["Elsa - Snow Queen"] == 15


def test_parse_decklist_with_bad_card_name(setup_test_files, mock_card_db):
    """Test parsing a decklist with a non-existent card."""
    # Arrange
    test_files = setup_test_files
    
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        parse_decklist(str(test_files["bad_card_file"]), mock_card_db)
    
    assert "Card not found in database" in str(excinfo.value)
    assert "Non-existent Card" in str(excinfo.value)


def test_parse_decklist_with_bad_card_count(setup_test_files, mock_card_db):
    """Test parsing a decklist with an incorrect card count."""
    # Arrange
    test_files = setup_test_files
    
    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        parse_decklist(str(test_files["bad_count_file"]), mock_card_db)
    
    assert "has 59 cards, but must have exactly 60" in str(excinfo.value)


def test_parse_missing_file(setup_test_files, mock_card_db):
    """Test parsing a non-existent file."""
    # Arrange
    test_files = setup_test_files
    
    # Act & Assert
    with pytest.raises(FileNotFoundError) as excinfo:
        parse_decklist(str(test_files["missing_file"]), mock_card_db)
    
    assert "Decklist file not found" in str(excinfo.value)


def test_parse_empty_file(setup_test_files, mock_card_db):
    """Test parsing an empty file."""
    # Arrange
    test_files = setup_test_files
    empty_file = test_files["test_dir"] / "empty_file.md"
    with open(empty_file, 'w', encoding='utf-8') as f:
        pass  # Create an empty file
    
    # Act
    decks = parse_decklist(str(empty_file), mock_card_db)
    
    # Assert
    assert len(decks) == 0


def test_parse_file_with_invalid_lines(setup_test_files, mock_card_db):
    """Test parsing a file with some invalid lines."""
    # Arrange
    test_files = setup_test_files
    invalid_lines_file = test_files["test_dir"] / "invalid_lines.md"
    with open(invalid_lines_file, 'w', encoding='utf-8') as f:
        f.write("This line should be ignored\n")
        f.write("[Valid Deck]\n")
        f.write("Invalid card line\n")
        f.write("20 Mickey Mouse - Brave Little Tailor\n")
        f.write("20 Maleficent - Mistress of Evil\n")
        f.write("20 Stitch - Rock Star\n")
    
    # Act
    decks = parse_decklist(str(invalid_lines_file), mock_card_db)
    
    # Assert
    assert len(decks) == 1
    assert decks[0]["name"] == "Valid Deck"
    assert len(decks[0]["cards"]) == 60  # Only valid card lines should be counted
