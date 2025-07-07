"""
Card Database module for Lorcana Pro Simulator.

This module provides access to card data by downloading it if necessary
and caching it locally.
"""
import json
import logging
from pathlib import Path
import requests
from requests.exceptions import RequestException

from src.config import CARDS_DATABASE_PATH, COMMUNITY_CARDS_URL, DATA_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CardDatabase:
    """
    Manages access to card data for the Lorcana Pro Simulator.
    
    This class ensures the application has access to card data by downloading
    it if necessary and caching it locally.
    """
    
    def __init__(self):
        """
        Initialize the CardDatabase.
        
        Checks for the existence of the local cards.json file.
        If it doesn't exist, downloads it from the configured URL.
        Loads the JSON data into a dictionary.
        """
        self.cards = {}
        
        # Ensure data directory exists
        DATA_DIR.mkdir(exist_ok=True, parents=True)
        
        # Check if cards.json exists
        if not CARDS_DATABASE_PATH.exists():
            try:
                self._download_cards()
            except RequestException as e:
                logger.error(f"Failed to download card data: {e}")
                raise RuntimeError("Could not initialize card database. Check your internet connection.") from e
        
        # Load cards from the JSON file
        self._load_cards()
    
    def _download_cards(self):
        """
        Download card data from the configured URL and save it locally.
        
        Raises:
            RequestException: If the download fails.
        """
        logger.info(f"Downloading card data from {COMMUNITY_CARDS_URL}")
        response = requests.get(COMMUNITY_CARDS_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Get JSON data from response
        try:
            card_data = response.json()
        except ValueError:
            # If response is not JSON, try to parse the text
            logger.warning("Response was not JSON format, attempting to parse text")
            card_data = json.loads(response.text)
        
        # Save the downloaded data
        with open(CARDS_DATABASE_PATH, 'w', encoding='utf-8') as f:
            json.dump(card_data, f, indent=2)
        
        logger.info(f"Card data successfully downloaded to {CARDS_DATABASE_PATH}")
    
    def _load_cards(self):
        """
        Load card data from the local JSON file into the cards dictionary.
        
        Cards are indexed by name for quick lookup.
        """
        logger.info(f"Loading card data from {CARDS_DATABASE_PATH}")
        try:
            with open(CARDS_DATABASE_PATH, 'r', encoding='utf-8') as f:
                card_list = json.load(f)
            
            # Index cards by name
            self.cards = {card['name']: card for card in card_list}
            logger.info(f"Successfully loaded {len(self.cards)} cards")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error loading card data: {e}")
            raise RuntimeError("Card data file is corrupted or in an unexpected format.") from e
    
    def get_card(self, name):
        """
        Get card data for a single card by name.
        
        Args:
            name (str): The name of the card to retrieve.
            
        Returns:
            dict: The card data, or None if not found.
        """
        return self.cards.get(name)
