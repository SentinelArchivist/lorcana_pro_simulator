"""
Game Simulation for Lorcana Pro Simulator

This module provides the GameSimulation class that orchestrates a single game
between two AI players using the game_rules module to process moves.
"""

import copy
import random
from typing import Dict, List, Tuple, Optional

from src.ai_player import AIPlayer
import src.game_rules as game_rules


class GameSimulation:
    """
    Simulates a single game of Lorcana between two AI players.
    
    This class is responsible for:
    1. Initializing the game state (shuffling decks, drawing hands)
    2. Handling the mulligan phase
    3. Running the main game loop until a winner is determined
    4. Recording the game log and determining the winner
    """
    
    def __init__(self, deck1: List[Dict], deck2: List[Dict], player1: AIPlayer, player2: AIPlayer):
        """
        Initialize a game simulation with two decks and two AI players.
        
        Args:
            deck1: List of card objects for player 1's deck
            deck2: List of card objects for player 2's deck
            player1: AI player object for player 1
            player2: AI player object for player 2
        """
        self.deck1 = copy.deepcopy(deck1)
        self.deck2 = copy.deepcopy(deck2)
        self.player1 = player1
        self.player2 = player2
        self.game_state = None
        self.winner = None
        self.game_log = []
    
    def run(self) -> Dict:
        """
        Run a complete game simulation from start to finish.
        
        Returns:
            A dictionary containing the winner's name and the full game log
        """
        # Initialize the game state
        self._initialize_game()
        
        # Handle mulligan phase
        self._handle_mulligan_phase()
        
        # Main game loop (turn-based)
        while not self._is_game_over():
            # Get the active player
            active_player_index = self.game_state["active_player_index"]
            active_player = self.player1 if active_player_index == 0 else self.player2
            
            # Draw a card at the start of the turn (except for the first player's first turn)
            if len(self.game_log) > 0:
                drawn_card = self._draw_card(active_player_index)
                self.game_state = game_rules.start_turn_phase(self.game_state, drawn_card)
            
            # Inner loop for multiple actions within a turn
            turn_continues = True
            while turn_continues and not self._is_game_over():
                # Get valid actions for the current state
                valid_actions = game_rules.get_valid_actions(self.game_state)
                
                # Let the AI choose an action
                chosen_action = active_player.choose_action(self.game_state, valid_actions)
                
                # Apply the action to the game state
                self.game_state = game_rules.apply_action(self.game_state, chosen_action)
                
                # Record the action in the game log
                self.game_log.append(chosen_action)
                
                # Check if the player chose to pass the turn
                if chosen_action["action_type"] == "PASS_TURN":
                    turn_continues = False
                
                # Check if the game is over after this action
                if self._is_game_over():
                    break
        
        # Determine the winner
        self._determine_winner()
        
        # Return the game results
        return {
            "winner": self.winner,
            "game_log": self.game_log
        }
    
    def _initialize_game(self) -> None:
        """
        Initialize the game state with shuffled decks and initial hands.
        """
        # Shuffle the decks
        random.shuffle(self.deck1)
        random.shuffle(self.deck2)
        
        # Create initial hands (7 cards each)
        hand1 = [self.deck1.pop() for _ in range(7)]
        hand2 = [self.deck2.pop() for _ in range(7)]
        
        # Create the initial game state
        self.game_state = {
            "turn_number": 1,
            "active_player_index": 0,  # Player 1 goes first
            "players": [
                {
                    "name": self.player1.name,
                    "lore": 0,
                    "deck_size": len(self.deck1),
                    "hand": hand1,
                    "discard_pile": [],
                    "inkwell_size": 0,
                    "inkwell_exerted": 0,
                    "has_inked_this_turn": False,
                    "board": []
                },
                {
                    "name": self.player2.name,
                    "lore": 0,
                    "deck_size": len(self.deck2),
                    "hand": hand2,
                    "discard_pile": [],
                    "inkwell_size": 0,
                    "inkwell_exerted": 0,
                    "has_inked_this_turn": False,
                    "board": []
                }
            ],
            "game_log": []
        }
    
    def _handle_mulligan_phase(self) -> None:
        """
        Handle the mulligan phase for both players.
        """
        # Player 1 mulligan
        if self.player1.handle_mulligan(self.game_state["players"][0]["hand"]):
            self._perform_mulligan(0)
        
        # Player 2 mulligan
        if self.player2.handle_mulligan(self.game_state["players"][1]["hand"]):
            self._perform_mulligan(1)
    
    def _perform_mulligan(self, player_index: int) -> None:
        """
        Perform a mulligan for the specified player.
        
        Args:
            player_index: The index of the player performing the mulligan
        """
        player = self.game_state["players"][player_index]
        deck = self.deck1 if player_index == 0 else self.deck2
        
        # Return cards to deck
        for card in player["hand"]:
            deck.append(card)
        
        # Shuffle deck
        random.shuffle(deck)
        
        # Draw new hand (7 cards)
        player["hand"] = [deck.pop() for _ in range(7)]
        player["deck_size"] = len(deck)
    
    def _draw_card(self, player_index: int) -> Optional[Dict]:
        """
        Draw a card from the player's deck.
        
        Args:
            player_index: The index of the player drawing a card
            
        Returns:
            The drawn card, or None if the deck is empty
        """
        deck = self.deck1 if player_index == 0 else self.deck2
        
        if len(deck) > 0:
            return deck.pop()
        return None
    
    def _is_game_over(self) -> bool:
        """
        Check if the game is over (a player has reached 20 lore).
        
        Returns:
            True if the game is over, False otherwise
        """
        return (self.game_state["players"][0]["lore"] >= 20 or 
                self.game_state["players"][1]["lore"] >= 20)
    
    def _determine_winner(self) -> None:
        """
        Determine the winner of the game.
        """
        if self.game_state["players"][0]["lore"] >= 20:
            self.winner = self.player1.name
        elif self.game_state["players"][1]["lore"] >= 20:
            self.winner = self.player2.name
        else:
            self.winner = None  # No winner yet
