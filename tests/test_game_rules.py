"""
Tests for the Lorcana game rules engine.

This module contains unit tests for the game_rules.py module, which implements
the core game rules for Disney Lorcana.
"""

import copy
import unittest
from src.game_rules import start_turn_phase, apply_action, get_valid_actions


class TestGameRules(unittest.TestCase):
    """Test cases for the game rules engine."""

    def setUp(self):
        """Set up a basic game state for testing."""
        self.game_state = {
            "turn_number": 1,
            "active_player_index": 0,
            "players": [
                {
                    "name": "Player 1",
                    "lore": 0,
                    "deck_size": 40,
                    "hand": [
                        {
                            "name": "Mickey Mouse - Brave Little Tailor",
                            "cost": 3,
                            "inkable": True,
                            "color": "Amber",
                            "type": "Character",
                            "subtypes": ["Hero"],
                            "attack": 2,
                            "defense": 3,
                            "lore": 2,
                            "abilities": ["First appearance - Draw a card."]
                        },
                        {
                            "name": "Flynn Rider - Charming Thief",
                            "cost": 2,
                            "inkable": True,
                            "color": "Amethyst",
                            "type": "Character",
                            "subtypes": ["Rogue"],
                            "attack": 1,
                            "defense": 2,
                            "lore": 1,
                            "abilities": []
                        },
                        {
                            "name": "Steal the Crown",
                            "cost": 1,
                            "inkable": True,
                            "color": "Amethyst",
                            "type": "Action",
                            "subtypes": [],
                            "attack": None,
                            "defense": None,
                            "lore": None,
                            "abilities": ["Draw a card."]
                        }
                    ],
                    "discard_pile": [],
                    "inkwell_size": 3,
                    "inkwell_exerted": 0,
                    "has_inked_this_turn": False,
                    "board": [
                        {
                            "card": {
                                "name": "Maleficent - Mistress of Evil",
                                "cost": 5,
                                "inkable": True,
                                "color": "Amethyst",
                                "type": "Character",
                                "subtypes": ["Villain", "Sorcerer"],
                                "attack": 4,
                                "defense": 5,
                                "lore": 3,
                                "abilities": ["Evasive"]
                            },
                            "exerted": True,
                            "damage": 0,
                            "can_act_this_turn": False
                        }
                    ]
                },
                {
                    "name": "Player 2",
                    "lore": 0,
                    "deck_size": 38,
                    "hand": [
                        {
                            "name": "Ariel - Curious Collector",
                            "cost": 2,
                            "inkable": True,
                            "color": "Ruby",
                            "type": "Character",
                            "subtypes": ["Princess"],
                            "attack": 1,
                            "defense": 2,
                            "lore": 2,
                            "abilities": []
                        }
                    ],
                    "discard_pile": [],
                    "inkwell_size": 2,
                    "inkwell_exerted": 0,
                    "has_inked_this_turn": False,
                    "board": [
                        {
                            "card": {
                                "name": "Simba - Rightful King",
                                "cost": 4,
                                "inkable": True,
                                "color": "Ruby",
                                "type": "Character",
                                "subtypes": ["Hero", "King"],
                                "attack": 3,
                                "defense": 4,
                                "lore": 2,
                                "abilities": []
                            },
                            "exerted": False,
                            "damage": 0,
                            "can_act_this_turn": True
                        }
                    ]
                }
            ],
            "game_log": []
        }
        
        # Sample card for draw tests
        self.drawn_card = {
            "name": "Genie - Phenomenal Cosmic Power",
            "cost": 4,
            "inkable": True,
            "color": "Sapphire",
            "type": "Character",
            "subtypes": ["Storyborn"],
            "attack": 3,
            "defense": 3,
            "lore": 2,
            "abilities": ["When you play this character, ready another character."]
        }

    def test_start_turn_phase(self):
        """Test the start_turn_phase function."""
        # Set has_inked_this_turn to True to verify it gets reset
        self.game_state["players"][0]["has_inked_this_turn"] = True
        
        # Test with a valid drawn card
        new_state = start_turn_phase(self.game_state, self.drawn_card)
        
        # Verify the state is a new object
        self.assertIsNot(new_state, self.game_state)
        
        # Check that the active player's cards are ready
        active_player = new_state["players"][0]
        self.assertEqual(active_player["inkwell_exerted"], 0)
        
        # Check that the board card is ready and can act
        board_card = active_player["board"][0]
        self.assertFalse(board_card["exerted"])
        self.assertTrue(board_card["can_act_this_turn"])
        
        # Check that has_inked_this_turn was reset
        self.assertFalse(active_player["has_inked_this_turn"])
        
        # Check that the drawn card was added to hand
        self.assertEqual(len(active_player["hand"]), 4)
        self.assertEqual(active_player["hand"][3]["name"], "Genie - Phenomenal Cosmic Power")
        
        # Check that the deck size was decremented
        self.assertEqual(active_player["deck_size"], 39)
        
        # Test with no drawn card (empty deck)
        empty_deck_state = copy.deepcopy(self.game_state)
        empty_deck_state["players"][0]["deck_size"] = 0
        empty_deck_state["players"][0]["has_inked_this_turn"] = True
        
        new_state = start_turn_phase(empty_deck_state, None)
        
        # Check that no card was added to hand
        active_player = new_state["players"][0]
        self.assertEqual(len(active_player["hand"]), 3)
        
        # Check that the deck size remains 0
        self.assertEqual(active_player["deck_size"], 0)
        
        # Check that has_inked_this_turn was reset even with no card drawn
        self.assertFalse(active_player["has_inked_this_turn"])

    def test_apply_action_pass_turn(self):
        """Test the apply_action function with PASS_TURN action."""
        action = {
            "action_type": "PASS_TURN",
            "source_card": None,
            "target_card": None,
            "player_index": 0
        }
        
        new_state = apply_action(self.game_state, action)
        
        # Verify the active player has changed
        self.assertEqual(new_state["active_player_index"], 1)
        
        # Pass turn again
        action["player_index"] = 1
        new_state = apply_action(new_state, action)
        
        # Verify player 0 is active again and turn number increased
        self.assertEqual(new_state["active_player_index"], 0)
        self.assertEqual(new_state["turn_number"], 2)
        
        # Verify no other state changes occurred
        self.assertEqual(len(new_state["players"][0]["hand"]), 3)
        self.assertEqual(len(new_state["players"][0]["board"]), 1)
        self.assertEqual(new_state["players"][0]["inkwell_exerted"], 0)

    def test_apply_action_play_card(self):
        """Test the apply_action function with PLAY_CARD action."""
        # Test playing a character card with sufficient ink
        action = {
            "action_type": "PLAY_CARD",
            "source_card": "Flynn Rider - Charming Thief",
            "target_card": None,
            "player_index": 0
        }
        
        new_state = apply_action(self.game_state, action)
        
        # Verify the card was removed from hand
        player = new_state["players"][0]
        self.assertEqual(len(player["hand"]), 2)
        
        # Verify the card was added to the board
        self.assertEqual(len(player["board"]), 2)
        self.assertEqual(player["board"][1]["card"]["name"], "Flynn Rider - Charming Thief")
        
        # Verify the card has summoning sickness
        self.assertFalse(player["board"][1]["can_act_this_turn"])
        
        # Verify ink was exerted
        self.assertEqual(player["inkwell_exerted"], 2)
        
        # Test playing a card with insufficient ink
        action = {
            "action_type": "PLAY_CARD",
            "source_card": "Mickey Mouse - Brave Little Tailor",
            "target_card": None,
            "player_index": 0
        }
        
        # Modify the state to have insufficient ink
        insufficient_ink_state = copy.deepcopy(new_state)
        insufficient_ink_state["players"][0]["inkwell_exerted"] = 2
        
        result_state = apply_action(insufficient_ink_state, action)
        
        # Verify the state didn't change
        self.assertEqual(len(result_state["players"][0]["hand"]), 2)
        self.assertEqual(len(result_state["players"][0]["board"]), 2)
        self.assertEqual(result_state["players"][0]["inkwell_exerted"], 2)
        
        # Test playing an action card
        action = {
            "action_type": "PLAY_CARD",
            "source_card": "Steal the Crown",
            "target_card": None,
            "player_index": 0
        }
        
        # Reset the exerted ink
        action_card_state = copy.deepcopy(new_state)
        action_card_state["players"][0]["inkwell_exerted"] = 0
        
        result_state = apply_action(action_card_state, action)
        
        # Verify the action card was removed from hand
        player = result_state["players"][0]
        self.assertEqual(len(player["hand"]), 1)
        
        # Verify the action card was added to discard pile
        self.assertEqual(len(player["discard_pile"]), 1)
        self.assertEqual(player["discard_pile"][0]["name"], "Steal the Crown")
        
        # Verify ink was exerted
        self.assertEqual(player["inkwell_exerted"], 1)

    def test_apply_action_ink_card(self):
        """Test the apply_action function with INK_CARD action."""
        # Test inking a card when has_inked_this_turn is False
        action = {
            "action_type": "INK_CARD",
            "source_card": "Flynn Rider - Charming Thief",
            "target_card": None,
            "player_index": 0
        }
        
        new_state = apply_action(self.game_state, action)
        
        # Verify the card was removed from hand
        player = new_state["players"][0]
        self.assertEqual(len(player["hand"]), 2)
        
        # Verify the inkwell size increased
        self.assertEqual(player["inkwell_size"], 4)
        
        # Verify has_inked_this_turn was set to True
        self.assertTrue(player["has_inked_this_turn"])
        
        # Test trying to ink a second card in the same turn
        second_ink_action = {
            "action_type": "INK_CARD",
            "source_card": "Mickey Mouse - Brave Little Tailor",
            "target_card": None,
            "player_index": 0
        }
        
        second_state = apply_action(new_state, second_ink_action)
        
        # Verify no changes were made (can't ink twice in one turn)
        player = second_state["players"][0]
        self.assertEqual(len(player["hand"]), 2)  # Still 2 cards in hand
        self.assertEqual(player["inkwell_size"], 4)  # Inkwell size unchanged

    def test_apply_action_quest(self):
        """Test the apply_action function with QUEST action."""
        # First, ready the character on the board
        ready_state = copy.deepcopy(self.game_state)
        ready_state["players"][0]["board"][0]["exerted"] = False
        ready_state["players"][0]["board"][0]["can_act_this_turn"] = True
        
        action = {
            "action_type": "QUEST",
            "source_card": "Maleficent - Mistress of Evil",
            "target_card": None,
            "player_index": 0
        }
        
        new_state = apply_action(ready_state, action)
        
        # Verify the character is now exerted
        player = new_state["players"][0]
        self.assertTrue(player["board"][0]["exerted"])
        
        # Verify lore was gained
        self.assertEqual(player["lore"], 3)
        
        # Test questing with an exerted character (should fail)
        exerted_state = copy.deepcopy(new_state)
        
        result_state = apply_action(exerted_state, action)
        
        # Verify the state didn't change
        self.assertEqual(result_state["players"][0]["lore"], 3)

    def test_apply_action_challenge(self):
        """Test the apply_action function with CHALLENGE action."""
        # Test 1: Challenge that deals damage to both characters but doesn't banish either
        damage_state = copy.deepcopy(self.game_state)
        damage_state["players"][0]["board"][0]["exerted"] = False
        damage_state["players"][0]["board"][0]["can_act_this_turn"] = True
        # Set up attack/defense values for a non-banishing challenge
        damage_state["players"][0]["board"][0]["card"]["attack"] = 2  # Maleficent's attack
        damage_state["players"][0]["board"][0]["card"]["defense"] = 5  # Maleficent's defense
        damage_state["players"][0]["board"][0]["damage"] = 0
        damage_state["players"][1]["board"][0]["card"]["attack"] = 2  # Simba's attack
        damage_state["players"][1]["board"][0]["card"]["defense"] = 4  # Simba's defense
        damage_state["players"][1]["board"][0]["damage"] = 0
        
        action = {
            "action_type": "CHALLENGE",
            "source_card": "Maleficent - Mistress of Evil",
            "target_card": "Simba - Rightful King",
            "player_index": 0
        }
        
        damage_result = apply_action(damage_state, action)
        
        # Verify the attacker is now exerted
        player = damage_result["players"][0]
        self.assertTrue(player["board"][0]["exerted"])
        
        # Verify damage was applied to BOTH characters
        self.assertEqual(player["board"][0]["damage"], 2)  # Attacker took damage
        opponent = damage_result["players"][1]
        self.assertEqual(opponent["board"][0]["damage"], 2)  # Defender took damage
        
        # Test 2: Challenge that banishes only the defender
        defender_banish_state = copy.deepcopy(self.game_state)
        defender_banish_state["players"][0]["board"][0]["exerted"] = False
        defender_banish_state["players"][0]["board"][0]["can_act_this_turn"] = True
        # Set up attack/defense values for defender banishment only
        defender_banish_state["players"][0]["board"][0]["card"]["attack"] = 4  # Maleficent's attack
        defender_banish_state["players"][0]["board"][0]["card"]["defense"] = 5  # Maleficent's defense
        defender_banish_state["players"][0]["board"][0]["damage"] = 0
        defender_banish_state["players"][1]["board"][0]["card"]["attack"] = 2  # Simba's attack
        defender_banish_state["players"][1]["board"][0]["card"]["defense"] = 4  # Simba's defense
        defender_banish_state["players"][1]["board"][0]["damage"] = 0
        
        defender_banish_result = apply_action(defender_banish_state, action)
        
        # Verify the defender was removed from the board
        opponent = defender_banish_result["players"][1]
        self.assertEqual(len(opponent["board"]), 0)
        
        # Verify the defender was added to the discard pile
        self.assertEqual(len(opponent["discard_pile"]), 1)
        self.assertEqual(opponent["discard_pile"][0]["name"], "Simba - Rightful King")
        
        # Verify the attacker took damage but survived
        player = defender_banish_result["players"][0]
        self.assertEqual(player["board"][0]["damage"], 2)  # Attacker took damage
        self.assertEqual(len(player["board"]), 1)  # Attacker still on board
        
        # Test 3: Challenge that banishes only the attacker
        attacker_banish_state = copy.deepcopy(self.game_state)
        attacker_banish_state["players"][0]["board"][0]["exerted"] = False
        attacker_banish_state["players"][0]["board"][0]["can_act_this_turn"] = True
        # Set up attack/defense values for attacker banishment only
        attacker_banish_state["players"][0]["board"][0]["card"]["attack"] = 2  # Maleficent's attack
        attacker_banish_state["players"][0]["board"][0]["card"]["defense"] = 3  # Maleficent's defense
        attacker_banish_state["players"][0]["board"][0]["damage"] = 0
        attacker_banish_state["players"][1]["board"][0]["card"]["attack"] = 3  # Simba's attack
        attacker_banish_state["players"][1]["board"][0]["card"]["defense"] = 4  # Simba's defense
        attacker_banish_state["players"][1]["board"][0]["damage"] = 0
        
        attacker_banish_result = apply_action(attacker_banish_state, action)
        
        # Verify the attacker was removed from the board
        player = attacker_banish_result["players"][0]
        self.assertEqual(len(player["board"]), 0)
        
        # Verify the attacker was added to the discard pile
        self.assertEqual(len(player["discard_pile"]), 1)
        self.assertEqual(player["discard_pile"][0]["name"], "Maleficent - Mistress of Evil")
        
        # Verify the defender took damage but survived
        opponent = attacker_banish_result["players"][1]
        self.assertEqual(opponent["board"][0]["damage"], 2)  # Defender took damage
        self.assertEqual(len(opponent["board"]), 1)  # Defender still on board
        
        # Test 4: Challenge that banishes both characters (trade)
        trade_state = copy.deepcopy(self.game_state)
        trade_state["players"][0]["board"][0]["exerted"] = False
        trade_state["players"][0]["board"][0]["can_act_this_turn"] = True
        # Set up attack/defense values for mutual banishment
        trade_state["players"][0]["board"][0]["card"]["attack"] = 4  # Maleficent's attack
        trade_state["players"][0]["board"][0]["card"]["defense"] = 3  # Maleficent's defense
        trade_state["players"][0]["board"][0]["damage"] = 0
        trade_state["players"][1]["board"][0]["card"]["attack"] = 3  # Simba's attack
        trade_state["players"][1]["board"][0]["card"]["defense"] = 4  # Simba's defense
        trade_state["players"][1]["board"][0]["damage"] = 0
        
        trade_result = apply_action(trade_state, action)
        
        # Verify both characters were removed from the board
        player = trade_result["players"][0]
        opponent = trade_result["players"][1]
        self.assertEqual(len(player["board"]), 0)  # Attacker banished
        self.assertEqual(len(opponent["board"]), 0)  # Defender banished
        
        # Verify both characters were added to their respective discard piles
        self.assertEqual(len(player["discard_pile"]), 1)
        self.assertEqual(player["discard_pile"][0]["name"], "Maleficent - Mistress of Evil")
        self.assertEqual(len(opponent["discard_pile"]), 1)
        self.assertEqual(opponent["discard_pile"][0]["name"], "Simba - Rightful King")

    def test_get_valid_actions(self):
        """Test the get_valid_actions function."""
        # Make sure the active player's character can act
        test_state = copy.deepcopy(self.game_state)
        test_state["players"][0]["board"][0]["exerted"] = False
        test_state["players"][0]["board"][0]["can_act_this_turn"] = True
        
        valid_actions = get_valid_actions(test_state)
        
        # Check that we have the expected number of actions
        # 1 PASS_TURN + 3 PLAY_CARD (one for each card in hand) + 3 INK_CARD + 1 QUEST + 1 CHALLENGE
        self.assertEqual(len(valid_actions), 9)
        
        # Check that we have the expected action types
        action_types = [action["action_type"] for action in valid_actions]
        self.assertIn("PASS_TURN", action_types)
        self.assertIn("PLAY_CARD", action_types)
        self.assertIn("INK_CARD", action_types)
        self.assertIn("QUEST", action_types)
        self.assertIn("CHALLENGE", action_types)
        
        # Check that we have the expected number of each action type
        self.assertEqual(action_types.count("PASS_TURN"), 1)
        self.assertEqual(action_types.count("PLAY_CARD"), 3)  # One for each card in hand
        self.assertEqual(action_types.count("INK_CARD"), 3)   # One for each inkable card in hand
        self.assertEqual(action_types.count("QUEST"), 1)      # One for the ready character
        self.assertEqual(action_types.count("CHALLENGE"), 1)  # One for the ready character
        
        # Test with insufficient ink
        insufficient_ink_state = copy.deepcopy(test_state)
        insufficient_ink_state["players"][0]["inkwell_size"] = 1  # Only 1 ink available
        
        valid_actions = get_valid_actions(insufficient_ink_state)
        
        # Check that expensive cards can't be played
        play_card_actions = [action for action in valid_actions if action["action_type"] == "PLAY_CARD"]
        play_card_names = [action["source_card"] for action in play_card_actions]
        
        # Only the 1-cost card should be playable
        self.assertIn("Steal the Crown", play_card_names)
        self.assertNotIn("Mickey Mouse - Brave Little Tailor", play_card_names)  # 3-cost
        self.assertNotIn("Flynn Rider - Charming Thief", play_card_names)       # 2-cost
        
        # Test with has_inked_this_turn = True
        inked_state = copy.deepcopy(test_state)
        inked_state["players"][0]["has_inked_this_turn"] = True
        
        valid_actions = get_valid_actions(inked_state)
        
        # Check that INK_CARD actions are not available when player has already inked this turn
        action_types = [action["action_type"] for action in valid_actions]
        self.assertNotIn("INK_CARD", action_types)
        
        # Verify we still have the other action types
        self.assertIn("PASS_TURN", action_types)
        self.assertIn("PLAY_CARD", action_types)
        self.assertIn("QUEST", action_types)
        self.assertIn("CHALLENGE", action_types)
        
        # Test with a character that has summoning sickness
        sickness_state = copy.deepcopy(self.game_state)
        sickness_state["players"][0]["board"][0]["exerted"] = False
        sickness_state["players"][0]["board"][0]["can_act_this_turn"] = False
        
        valid_actions = get_valid_actions(sickness_state)
        
        # Verify no QUEST or CHALLENGE actions are available
        quest_actions = [a for a in valid_actions if a["action_type"] == "QUEST"]
        challenge_actions = [a for a in valid_actions if a["action_type"] == "CHALLENGE"]
        self.assertEqual(len(quest_actions), 0)
        self.assertEqual(len(challenge_actions), 0)


if __name__ == "__main__":
    unittest.main()
