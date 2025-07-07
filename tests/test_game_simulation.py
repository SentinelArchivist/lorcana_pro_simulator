"""
Tests for the GameSimulation class.

This module contains unit tests for the GameSimulation class, which orchestrates
a single game between two AI players.
"""

import unittest
from unittest.mock import MagicMock, patch
import copy
from typing import Dict, List

from src.ai_player import AIPlayer
from src.game_simulation import GameSimulation


class TestGameSimulation(unittest.TestCase):
    """Test cases for the GameSimulation class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample cards for testing
        self.sample_character_card = {
            "name": "Test Character",
            "cost": 3,
            "inkable": True,
            "color": "Amber",
            "type": "Character",
            "subtypes": ["Hero"],
            "attack": 2,
            "defense": 3,
            "lore": 2,
            "abilities": ["Test ability"]
        }
        
        self.sample_action_card = {
            "name": "Test Action",
            "cost": 2,
            "inkable": True,
            "color": "Ruby",
            "type": "Action",
            "subtypes": [],
            "attack": None,
            "defense": None,
            "lore": None,
            "abilities": ["Test action ability"]
        }
        
        # Create sample decks
        self.deck1 = [copy.deepcopy(self.sample_character_card) for _ in range(15)]
        self.deck1.extend([copy.deepcopy(self.sample_action_card) for _ in range(15)])
        
        self.deck2 = [copy.deepcopy(self.sample_character_card) for _ in range(15)]
        self.deck2.extend([copy.deepcopy(self.sample_action_card) for _ in range(15)])
        
        # Create mock AI players
        self.player1 = MagicMock(spec=AIPlayer)
        self.player1.name = "TestPlayer1"
        
        self.player2 = MagicMock(spec=AIPlayer)
        self.player2.name = "TestPlayer2"
    
    def test_initialization(self):
        """Test that the GameSimulation initializes correctly."""
        # Create a game simulation
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Check that the decks and players are set correctly
        self.assertEqual(len(simulation.deck1), 30)
        self.assertEqual(len(simulation.deck2), 30)
        self.assertEqual(simulation.player1, self.player1)
        self.assertEqual(simulation.player2, self.player2)
        self.assertIsNone(simulation.game_state)
        self.assertIsNone(simulation.winner)
        self.assertEqual(simulation.game_log, [])
    
    @patch('random.shuffle')
    def test_initialize_game(self, mock_shuffle):
        """Test that the game state is initialized correctly."""
        # Create a game simulation
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Initialize the game
        simulation._initialize_game()
        
        # Check that the decks were shuffled
        self.assertEqual(mock_shuffle.call_count, 2)
        
        # Check that the game state was created correctly
        self.assertIsNotNone(simulation.game_state)
        self.assertEqual(simulation.game_state["turn_number"], 1)
        self.assertEqual(simulation.game_state["active_player_index"], 0)
        
        # Check player 1's state
        player1_state = simulation.game_state["players"][0]
        self.assertEqual(player1_state["name"], "TestPlayer1")
        self.assertEqual(player1_state["lore"], 0)
        self.assertEqual(player1_state["deck_size"], 23)  # 30 - 7 cards drawn
        self.assertEqual(len(player1_state["hand"]), 7)
        self.assertEqual(player1_state["discard_pile"], [])
        self.assertEqual(player1_state["inkwell_size"], 0)
        self.assertEqual(player1_state["inkwell_exerted"], 0)
        self.assertEqual(player1_state["board"], [])
        
        # Check player 2's state
        player2_state = simulation.game_state["players"][1]
        self.assertEqual(player2_state["name"], "TestPlayer2")
        self.assertEqual(player2_state["lore"], 0)
        self.assertEqual(player2_state["deck_size"], 23)  # 30 - 7 cards drawn
        self.assertEqual(len(player2_state["hand"]), 7)
        self.assertEqual(player2_state["discard_pile"], [])
        self.assertEqual(player2_state["inkwell_size"], 0)
        self.assertEqual(player2_state["inkwell_exerted"], 0)
        self.assertEqual(player2_state["board"], [])
    
    def test_handle_mulligan_phase_no_mulligans(self):
        """Test the mulligan phase when both players keep their hands."""
        # Create a game simulation
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Initialize the game
        simulation._initialize_game()
        
        # Set up player decisions
        self.player1.handle_mulligan.return_value = False
        self.player2.handle_mulligan.return_value = False
        
        # Save the initial hands
        initial_hand1 = copy.deepcopy(simulation.game_state["players"][0]["hand"])
        initial_hand2 = copy.deepcopy(simulation.game_state["players"][1]["hand"])
        
        # Handle mulligan phase
        simulation._handle_mulligan_phase()
        
        # Check that the players were asked about mulligans
        self.player1.handle_mulligan.assert_called_once_with(initial_hand1)
        self.player2.handle_mulligan.assert_called_once_with(initial_hand2)
        
        # Check that the hands didn't change
        self.assertEqual(simulation.game_state["players"][0]["hand"], initial_hand1)
        self.assertEqual(simulation.game_state["players"][1]["hand"], initial_hand2)
    
    def test_handle_mulligan_phase_with_mulligans(self):
        """Test the mulligan phase when both players mulligan."""
        # Create a game simulation
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Initialize the game
        simulation._initialize_game()
        
        # Set up player decisions
        self.player1.handle_mulligan.return_value = True
        self.player2.handle_mulligan.return_value = True
        
        # Save the initial hands
        initial_hand1 = copy.deepcopy(simulation.game_state["players"][0]["hand"])
        initial_hand2 = copy.deepcopy(simulation.game_state["players"][1]["hand"])
        
        # Handle mulligan phase
        simulation._handle_mulligan_phase()
        
        # Check that the players were asked about mulligans
        self.player1.handle_mulligan.assert_called_once_with(initial_hand1)
        self.player2.handle_mulligan.assert_called_once_with(initial_hand2)
        
        # Check that the hands changed
        self.assertNotEqual(simulation.game_state["players"][0]["hand"], initial_hand1)
        self.assertNotEqual(simulation.game_state["players"][1]["hand"], initial_hand2)
        
        # Check that the new hands have 7 cards each
        self.assertEqual(len(simulation.game_state["players"][0]["hand"]), 7)
        self.assertEqual(len(simulation.game_state["players"][1]["hand"]), 7)
    
    def test_run_game_to_completion(self):
        """Test running a complete game simulation with multi-action turns."""
        # Create a game simulation with mocked players
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Set up mocks for no mulligans
        self.player1.handle_mulligan.return_value = False
        self.player2.handle_mulligan.return_value = False
        
        # Create a controlled sequence of actions for each player
        # Player 1's first turn: INK, PLAY, QUEST, PASS
        # Player 2's first turn: INK, PLAY, PASS
        # Player 1's second turn: QUEST, PASS
        # Player 2's second turn: QUEST, PASS
        # Player 1's third turn: QUEST (reaches 20 lore and wins)
        
        # Define action templates
        ink_action_p1 = {
            "action_type": "INK_CARD",
            "source_card": "Test Action",
            "target_card": None,
            "player_index": 0
        }
        
        play_action_p1 = {
            "action_type": "PLAY_CARD",
            "source_card": "Test Character",
            "target_card": None,
            "player_index": 0
        }
        
        quest_action_p1 = {
            "action_type": "QUEST",
            "source_card": "Test Character",
            "target_card": None,
            "player_index": 0
        }
        
        pass_action_p1 = {
            "action_type": "PASS_TURN",
            "source_card": None,
            "target_card": None,
            "player_index": 0
        }
        
        ink_action_p2 = {
            "action_type": "INK_CARD",
            "source_card": "Test Action",
            "target_card": None,
            "player_index": 1
        }
        
        play_action_p2 = {
            "action_type": "PLAY_CARD",
            "source_card": "Test Character",
            "target_card": None,
            "player_index": 1
        }
        
        quest_action_p2 = {
            "action_type": "QUEST",
            "source_card": "Test Character",
            "target_card": None,
            "player_index": 1
        }
        
        pass_action_p2 = {
            "action_type": "PASS_TURN",
            "source_card": None,
            "target_card": None,
            "player_index": 1
        }
        
        # Set up the action sequences
        player1_actions = [ink_action_p1, play_action_p1, quest_action_p1, pass_action_p1,  # Turn 1
                          quest_action_p1, pass_action_p1,  # Turn 2
                          quest_action_p1]  # Turn 3 (wins)
        
        player2_actions = [ink_action_p2, play_action_p2, pass_action_p2,  # Turn 1
                          quest_action_p2, pass_action_p2]  # Turn 2
        
        # Set up the choose_action mocks
        self.player1.choose_action.side_effect = player1_actions
        self.player2.choose_action.side_effect = player2_actions
        
        # Mock the game state directly to control the flow
        # Initialize the game state manually
        simulation._initialize_game = MagicMock()
        simulation.game_state = {
            "turn_number": 1,
            "active_player_index": 0,  # Player 1 goes first
            "players": [
                {
                    "name": "TestPlayer1",
                    "lore": 0,
                    "deck_size": 23,
                    "hand": [self.sample_action_card, self.sample_character_card],
                    "discard_pile": [],
                    "inkwell_size": 0,
                    "inkwell_exerted": 0,
                    "has_inked_this_turn": False,
                    "board": []
                },
                {
                    "name": "TestPlayer2",
                    "lore": 0,
                    "deck_size": 23,
                    "hand": [self.sample_action_card, self.sample_character_card],
                    "discard_pile": [],
                    "inkwell_size": 0,
                    "inkwell_exerted": 0,
                    "has_inked_this_turn": False,
                    "board": []
                }
            ],
            "game_log": []
        }
        
        # Mock the game_rules module
        with patch('src.game_rules.get_valid_actions') as mock_get_valid_actions, \
             patch('src.game_rules.apply_action') as mock_apply_action, \
             patch('src.game_rules.start_turn_phase') as mock_start_turn:
            
            # Set up mock for valid actions - always return all possible actions
            mock_get_valid_actions.return_value = [
                ink_action_p1, play_action_p1, quest_action_p1, pass_action_p1
            ]
            
            # Set up mock for apply_action to handle different action types
            def side_effect_apply_action(state, action):
                new_state = copy.deepcopy(state)
                action_type = action["action_type"]
                player_index = action["player_index"]
                
                if action_type == "INK_CARD":
                    # Simulate inking a card
                    new_state["players"][player_index]["inkwell_size"] += 1
                    new_state["players"][player_index]["has_inked_this_turn"] = True
                
                elif action_type == "PLAY_CARD":
                    # Simulate playing a character card
                    new_state["players"][player_index]["board"].append({
                        "card": self.sample_character_card,
                        "exerted": False,
                        "damage": 0,
                        "can_act_this_turn": True
                    })
                
                elif action_type == "QUEST":
                    # Simulate questing with a character
                    new_state["players"][player_index]["lore"] += 6  # Increase lore gain for faster test
                    
                    # Player 1 wins after 3 quests (18 lore)
                    if player_index == 0 and new_state["players"][0]["lore"] >= 18:
                        new_state["players"][0]["lore"] = 20
                
                elif action_type == "PASS_TURN":
                    # Switch active player when passing turn
                    new_state["active_player_index"] = 1 - new_state["active_player_index"]
                    
                    # Reset has_inked_this_turn for the next player
                    next_player_index = new_state["active_player_index"]
                    new_state["players"][next_player_index]["has_inked_this_turn"] = False
                
                # Add the action to the game log
                new_state["game_log"].append(action)
                
                return new_state
            
            mock_apply_action.side_effect = side_effect_apply_action
            
            # Set up mock for start_turn_phase to pass through
            mock_start_turn.side_effect = lambda state, card: state
            
            # Run the simulation
            result = simulation.run()
            
            # Check that the game ended with a winner
            self.assertEqual(result["winner"], "TestPlayer1")
            
            # Check that both AI players were asked to choose actions
            self.assertEqual(self.player1.choose_action.call_count, len(player1_actions))
            self.assertEqual(self.player2.choose_action.call_count, len(player2_actions))
            
            # Verify that the game log contains all actions
            expected_actions = len(player1_actions) + len(player2_actions)
            self.assertEqual(len(result["game_log"]), expected_actions)
            
            # Verify that the game log contains multiple actions per turn
            # Count the number of PASS_TURN actions to determine turn count
            pass_turn_count = sum(1 for action in result["game_log"] if action["action_type"] == "PASS_TURN")
            
            # There should be more total actions than just pass turns
            self.assertGreater(len(result["game_log"]), pass_turn_count)
            
            # Verify that each player took multiple actions in a single turn
            # by checking that there are actions between PASS_TURN actions
            pass_indices = [i for i, action in enumerate(result["game_log"]) 
                           if action["action_type"] == "PASS_TURN"]
            
            # Check the first turn (from start to first PASS_TURN)
            first_turn_actions = result["game_log"][:pass_indices[0]+1]
            self.assertGreater(len(first_turn_actions), 1)  # More than just PASS_TURN
            
            # Check second turn if available
            if len(pass_indices) > 1:
                second_turn_actions = result["game_log"][pass_indices[0]+1:pass_indices[1]+1]
                self.assertGreater(len(second_turn_actions), 1)  # More than just PASS_TURN
    
    def test_is_game_over(self):
        """Test the game over condition."""
        # Create a game simulation
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Initialize the game
        simulation._initialize_game()
        
        # Check that the game is not over initially
        self.assertFalse(simulation._is_game_over())
        
        # Set player 1's lore to 20
        simulation.game_state["players"][0]["lore"] = 20
        
        # Check that the game is over
        self.assertTrue(simulation._is_game_over())
        
        # Reset player 1's lore
        simulation.game_state["players"][0]["lore"] = 0
        
        # Set player 2's lore to 20
        simulation.game_state["players"][1]["lore"] = 20
        
        # Check that the game is over
        self.assertTrue(simulation._is_game_over())
    
    def test_determine_winner(self):
        """Test determining the winner."""
        # Create a game simulation
        simulation = GameSimulation(self.deck1, self.deck2, self.player1, self.player2)
        
        # Initialize the game
        simulation._initialize_game()
        
        # Set player 1's lore to 20
        simulation.game_state["players"][0]["lore"] = 20
        
        # Determine the winner
        simulation._determine_winner()
        
        # Check that player 1 is the winner
        self.assertEqual(simulation.winner, "TestPlayer1")
        
        # Reset player 1's lore and set player 2's lore to 20
        simulation.game_state["players"][0]["lore"] = 0
        simulation.game_state["players"][1]["lore"] = 20
        
        # Determine the winner
        simulation._determine_winner()
        
        # Check that player 2 is the winner
        self.assertEqual(simulation.winner, "TestPlayer2")
        
        # Reset both players' lore
        simulation.game_state["players"][0]["lore"] = 0
        simulation.game_state["players"][1]["lore"] = 0
        
        # Determine the winner
        simulation._determine_winner()
        
        # Check that there is no winner
        self.assertIsNone(simulation.winner)


if __name__ == "__main__":
    unittest.main()
