"""
AI Player Interface for Lorcana Pro Simulator

This module defines the interface for AI players that can participate in Lorcana games.
"""

from abc import ABC, abstractmethod
from typing import Dict, List


class AIPlayer(ABC):
    """
    Abstract base class for AI players in the Lorcana Pro Simulator.
    
    All AI implementations must inherit from this class and implement the choose_action method.
    """
    
    def __init__(self, name: str):
        """
        Initialize an AI player.
        
        Args:
            name: The name of the AI player
        """
        self.name = name
    
    @abstractmethod
    def choose_action(self, game_state: Dict, valid_actions: List[Dict]) -> Dict:
        """
        Choose an action to take given the current game state and valid actions.
        
        Args:
            game_state: The current state of the game
            valid_actions: List of valid actions the player can take
            
        Returns:
            The chosen action as a dictionary
        """
        pass
    
    def handle_mulligan(self, initial_hand: List[Dict]) -> bool:
        """
        Decide whether to mulligan the initial hand.
        
        Args:
            initial_hand: The initial hand of cards
            
        Returns:
            True if the player wants to mulligan, False otherwise
        """
        # Default implementation always keeps the initial hand
        # Override this method in subclasses for more sophisticated behavior
        return False


class RandomAIPlayer(AIPlayer):
    """
    A simple AI player that makes random choices from the available valid actions.
    """
    
    def __init__(self, name: str):
        """
        Initialize a RandomAIPlayer.
        
        Args:
            name: The name of the AI player
        """
        super().__init__(name)
        import random
        self.random = random
    
    def choose_action(self, game_state: Dict, valid_actions: List[Dict]) -> Dict:
        """
        Choose a random action from the list of valid actions.
        
        Args:
            game_state: The current state of the game
            valid_actions: List of valid actions the player can take
            
        Returns:
            A randomly chosen action
        """
        return self.random.choice(valid_actions)
    
    def handle_mulligan(self, initial_hand: List[Dict]) -> bool:
        """
        Randomly decide whether to mulligan the initial hand.
        
        Args:
            initial_hand: The initial hand of cards
            
        Returns:
            True if the player wants to mulligan, False otherwise
        """
        return self.random.choice([True, False])
