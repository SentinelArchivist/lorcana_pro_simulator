"""
Deck Parser module for Lorcana Pro Simulator.

This module provides functionality to parse decklist files in a specific format
and convert them into deck objects that can be used by the simulator.
"""
import logging
import re
from pathlib import Path
from typing import List, Dict, Any

from src.card_database import CardDatabase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_decklist(filepath: str, card_db: CardDatabase) -> List[Dict[str, Any]]:
    """
    Parse a decklist file and convert it into a list of deck objects.
    
    The file format is:
    - Deck names are on lines like [Deck Name]
    - Cards are on lines like 4 Card Name
    - Decks are separated by one or more blank lines
    
    Args:
        filepath (str): Path to the decklist file
        card_db (CardDatabase): Card database to validate and fetch card data
        
    Returns:
        List[Dict[str, Any]]: List of deck objects, each with a name and list of cards
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If a card is not found in the database or a deck doesn't have exactly 60 cards
    """
    file_path = Path(filepath)
    
    # Check if file exists
    if not file_path.exists():
        logger.error(f"Decklist file not found: {filepath}")
        raise FileNotFoundError(f"Decklist file not found: {filepath}")
    
    decks = []
    current_deck = None
    current_cards = []
    
    # Regular expressions for parsing
    deck_name_pattern = re.compile(r'^\[(.*)\]$')
    card_pattern = re.compile(r'^(\d+)\s+(.+)$')
    
    logger.info(f"Parsing decklist file: {filepath}")
    
    # Read the file line by line
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                # If we have a deck in progress, save it before moving on
                if current_deck is not None and current_cards:
                    # Validate deck size
                    if len(current_cards) != 60:
                        logger.error(f"Deck '{current_deck}' has {len(current_cards)} cards, but must have exactly 60")
                        raise ValueError(f"Deck '{current_deck}' has {len(current_cards)} cards, but must have exactly 60")
                    
                    decks.append({
                        "name": current_deck,
                        "cards": current_cards
                    })
                    current_deck = None
                    current_cards = []
                continue
            
            # Check if this line is a deck name
            deck_match = deck_name_pattern.match(line)
            if deck_match:
                # If we already have a deck in progress, save it before starting a new one
                if current_deck is not None and current_cards:
                    # Validate deck size
                    if len(current_cards) != 60:
                        logger.error(f"Deck '{current_deck}' has {len(current_cards)} cards, but must have exactly 60")
                        raise ValueError(f"Deck '{current_deck}' has {len(current_cards)} cards, but must have exactly 60")
                    
                    decks.append({
                        "name": current_deck,
                        "cards": current_cards
                    })
                    current_cards = []
                
                current_deck = deck_match.group(1).strip()
                logger.info(f"Found deck: {current_deck}")
                continue
            
            # Check if this line is a card entry
            card_match = card_pattern.match(line)
            if card_match and current_deck is not None:
                quantity = int(card_match.group(1))
                card_name = card_match.group(2).strip()
                
                # Validate card exists in database
                card_data = card_db.get_card(card_name)
                if card_data is None:
                    logger.error(f"Card not found in database: {card_name} (line {line_num})")
                    raise ValueError(f"Card not found in database: {card_name} (line {line_num})")
                
                # Add the specified quantity of this card to the deck
                current_cards.extend([card_data] * quantity)
                logger.debug(f"Added {quantity}x {card_name} to deck '{current_deck}'")
            elif current_deck is None:
                logger.warning(f"Ignoring card entry before deck name: {line} (line {line_num})")
            else:
                logger.warning(f"Ignoring invalid line: {line} (line {line_num})")
    
    # Don't forget to add the last deck if there is one
    if current_deck is not None and current_cards:
        # Validate deck size
        if len(current_cards) != 60:
            logger.error(f"Deck '{current_deck}' has {len(current_cards)} cards, but must have exactly 60")
            raise ValueError(f"Deck '{current_deck}' has {len(current_cards)} cards, but must have exactly 60")
        
        decks.append({
            "name": current_deck,
            "cards": current_cards
        })
    
    logger.info(f"Successfully parsed {len(decks)} decks from {filepath}")
    return decks
