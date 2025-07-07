"""
Configuration module for Lorcana Pro Simulator.

This module contains all global, non-sensitive constants used throughout the application.
No executable logic should be present in this file.
"""
from pathlib import Path

# Game rules constants
LORE_TO_WIN = 20
STARTING_HAND_SIZE = 7
MAX_DECK_SIZE = 60

# File system paths
DATA_DIR = Path(__file__).parent.parent / 'data'
CARDS_DATABASE_PATH = DATA_DIR / 'cards.json'

# External data sources
COMMUNITY_CARDS_URL = "https://lorcana-api.com/api/cards/all"  # Example URL, replace with actual source

# Output file names
DECK_ANALYSIS_CSV = 'deck_analysis.csv'
GAME_STATISTICS_CSV = 'game_statistics.csv'
CARD_USAGE_CSV = 'card_usage.csv'
