"""
Lorcana Game Rules Engine

This module provides pure, stateless functions that calculate game state transitions
according to the rules of Disney Lorcana. It is responsible for:
1. Handling the start-of-turn "Ready, Set, Draw" sequence
2. Applying player actions (play card, ink card, quest, challenge, pass turn)
3. Determining valid actions in a given game state

This module is entirely self-contained and unaware of the game loop, AI, or deck contents.
It only performs state changes as requested by the game simulation.
"""

import copy
from typing import Dict, List, Optional, Union


def start_turn_phase(game_state: Dict, drawn_card: Optional[Dict] = None) -> Dict:
    """
    Handles the start-of-turn "Ready, Set, Draw" sequence.
    
    Args:
        game_state: The current game state
        drawn_card: The card drawn from the deck (or None if deck is empty)
        
    Returns:
        The new game state after the start-of-turn phase is complete
    """
    # Create a deep copy to avoid modifying the original state
    new_state = copy.deepcopy(game_state)
    
    # Get the active player
    active_player_index = new_state["active_player_index"]
    active_player = new_state["players"][active_player_index]
    
    # Ready phase: Un-exert all cards in the inkwell
    active_player["inkwell_exerted"] = 0
    
    # Set phase: Ready all cards on the board and set can_act_this_turn to true
    for card_state in active_player["board"]:
        card_state["exerted"] = False
        card_state["can_act_this_turn"] = True
    
    # Reset the has_inked_this_turn flag for the active player
    active_player["has_inked_this_turn"] = False
    
    # Draw phase: Add the drawn card to the player's hand if provided
    if drawn_card is not None:
        active_player["hand"].append(drawn_card)
        active_player["deck_size"] -= 1
    
    return new_state


def apply_action(game_state: Dict, action: Dict) -> Dict:
    """
    Applies a player action to the game state.
    
    Args:
        game_state: The current game state
        action: The player action to apply
        
    Returns:
        The new game state after the action is applied
    """
    # Create a deep copy to avoid modifying the original state
    new_state = copy.deepcopy(game_state)
    
    # Process the action based on its type
    action_type = action["action_type"]
    player_index = action["player_index"]
    
    if action_type == "PASS_TURN":
        return _handle_pass_turn(new_state)
    elif action_type == "PLAY_CARD":
        return _handle_play_card(new_state, action, player_index)
    elif action_type == "INK_CARD":
        return _handle_ink_card(new_state, action, player_index)
    elif action_type == "QUEST":
        return _handle_quest(new_state, action, player_index)
    elif action_type == "CHALLENGE":
        return _handle_challenge(new_state, action, player_index)
    else:
        # Invalid action type
        return game_state


def get_valid_actions(game_state: Dict) -> List[Dict]:
    """
    Determines all legal moves a player can make in the current state.
    
    Args:
        game_state: The current game state
        
    Returns:
        A list of valid action dictionaries
    """
    valid_actions = []
    active_player_index = game_state["active_player_index"]
    active_player = game_state["players"][active_player_index]
    
    # PASS_TURN is always valid
    valid_actions.append({
        "action_type": "PASS_TURN",
        "source_card": None,
        "target_card": None,
        "player_index": active_player_index
    })
    
    # Check for valid INK_CARD actions
    # A player can only ink one card per turn
    if not active_player.get("has_inked_this_turn", False):
        for card in active_player["hand"]:
            if card["inkable"]:
                valid_actions.append({
                    "action_type": "INK_CARD",
                    "source_card": card["name"],
                    "target_card": None,
                    "player_index": active_player_index
                })
    
    # Check for valid PLAY_CARD actions
    available_ink = active_player["inkwell_size"] - active_player["inkwell_exerted"]
    for card in active_player["hand"]:
        if card["cost"] <= available_ink:
            valid_actions.append({
                "action_type": "PLAY_CARD",
                "source_card": card["name"],
                "target_card": None,
                "player_index": active_player_index
            })
    
    # Check for valid QUEST actions
    for i, board_card in enumerate(active_player["board"]):
        card = board_card["card"]
        # Characters can quest if they're not exerted and can act this turn
        if (card["type"] == "Character" and 
            not board_card["exerted"] and 
            board_card["can_act_this_turn"] and
            card["lore"] is not None and 
            card["lore"] > 0):
            valid_actions.append({
                "action_type": "QUEST",
                "source_card": card["name"],
                "target_card": None,
                "player_index": active_player_index
            })
    
    # Check for valid CHALLENGE actions
    opponent_index = 1 - active_player_index
    opponent = game_state["players"][opponent_index]
    
    for i, attacker in enumerate(active_player["board"]):
        attacker_card = attacker["card"]
        # Characters can challenge if they're not exerted and can act this turn
        if (attacker_card["type"] == "Character" and 
            not attacker["exerted"] and 
            attacker["can_act_this_turn"] and
            attacker_card["attack"] is not None and 
            attacker_card["attack"] > 0):
            
            for j, defender in enumerate(opponent["board"]):
                defender_card = defender["card"]
                if defender_card["type"] == "Character":
                    valid_actions.append({
                        "action_type": "CHALLENGE",
                        "source_card": attacker_card["name"],
                        "target_card": defender_card["name"],
                        "player_index": active_player_index
                    })
    
    return valid_actions


# Helper functions for apply_action

def _handle_pass_turn(game_state: Dict) -> Dict:
    """
    Handles the PASS_TURN action.
    
    Args:
        game_state: The current game state
        
    Returns:
        The new game state after passing the turn
    """
    # Switch the active player
    game_state["active_player_index"] = 1 - game_state["active_player_index"]
    
    # Increment turn number if we're back to player 0
    if game_state["active_player_index"] == 0:
        game_state["turn_number"] += 1
    
    return game_state


def _handle_play_card(game_state: Dict, action: Dict, player_index: int) -> Dict:
    """
    Handles the PLAY_CARD action.
    
    Args:
        game_state: The current game state
        action: The player action
        player_index: The index of the player performing the action
        
    Returns:
        The new game state after playing the card
    """
    player = game_state["players"][player_index]
    source_card_name = action["source_card"]
    
    # Find the card in the player's hand
    card_index = None
    card = None
    for i, hand_card in enumerate(player["hand"]):
        if hand_card["name"] == source_card_name:
            card_index = i
            card = hand_card
            break
    
    if card is None:
        # Card not found in hand
        return game_state
    
    # Check if player has enough ink
    available_ink = player["inkwell_size"] - player["inkwell_exerted"]
    if card["cost"] > available_ink:
        # Not enough ink
        return game_state
    
    # Exert the required amount of ink
    player["inkwell_exerted"] += card["cost"]
    
    # Remove the card from the hand
    player["hand"].pop(card_index)
    
    # Add the card to the board if it's a Character or Item
    if card["type"] in ["Character", "Item"]:
        player["board"].append({
            "card": card,
            "exerted": False,
            "damage": 0,
            "can_act_this_turn": False  # Characters have summoning sickness
        })
    else:  # Action card
        # Actions go to the discard pile after being played
        player["discard_pile"].append(card)
        # Action card effects would be handled here
        # For now, we're not implementing specific card effects
    
    # Add to game log
    game_state["game_log"].append(action)
    
    return game_state


def _handle_ink_card(game_state: Dict, action: Dict, player_index: int) -> Dict:
    """
    Handles the INK_CARD action.
    
    Args:
        game_state: The current game state
        action: The player action
        player_index: The index of the player performing the action
        
    Returns:
        The new game state after inking the card
    """
    player = game_state["players"][player_index]
    source_card_name = action["source_card"]
    
    # Check if player has already inked a card this turn
    if player["has_inked_this_turn"]:
        # Player can only ink one card per turn
        return game_state
    
    # Find the card in the player's hand
    card_index = None
    card = None
    for i, hand_card in enumerate(player["hand"]):
        if hand_card["name"] == source_card_name:
            card_index = i
            card = hand_card
            break
    
    if card is None or not card["inkable"]:
        # Card not found in hand or not inkable
        return game_state
    
    # Remove the card from the hand
    player["hand"].pop(card_index)
    
    # Increase the inkwell size
    player["inkwell_size"] += 1
    
    # Mark that the player has inked a card this turn
    player["has_inked_this_turn"] = True
    
    # Add to game log
    game_state["game_log"].append(action)
    
    return game_state


def _handle_quest(game_state: Dict, action: Dict, player_index: int) -> Dict:
    """
    Handles the QUEST action.
    
    Args:
        game_state: The current game state
        action: The player action
        player_index: The index of the player performing the action
        
    Returns:
        The new game state after questing
    """
    player = game_state["players"][player_index]
    source_card_name = action["source_card"]
    
    # Find the card on the player's board
    card_index = None
    board_card = None
    for i, bc in enumerate(player["board"]):
        if bc["card"]["name"] == source_card_name:
            card_index = i
            board_card = bc
            break
    
    if (board_card is None or 
        board_card["card"]["type"] != "Character" or 
        board_card["exerted"] or 
        not board_card["can_act_this_turn"] or
        board_card["card"]["lore"] is None or
        board_card["card"]["lore"] <= 0):
        # Invalid quest
        return game_state
    
    # Exert the character
    board_card["exerted"] = True
    
    # Gain lore
    player["lore"] += board_card["card"]["lore"]
    
    # Add to game log
    game_state["game_log"].append(action)
    
    return game_state


def _handle_challenge(game_state: Dict, action: Dict, player_index: int) -> Dict:
    """
    Handles the CHALLENGE action.
    
    Args:
        game_state: The current game state
        action: The player action
        player_index: The index of the player performing the action
        
    Returns:
        The new game state after challenging
    """
    player = game_state["players"][player_index]
    opponent_index = 1 - player_index
    opponent = game_state["players"][opponent_index]
    
    source_card_name = action["source_card"]
    target_card_name = action["target_card"]
    
    # Find the attacker on the player's board
    attacker_index = None
    attacker = None
    for i, bc in enumerate(player["board"]):
        if bc["card"]["name"] == source_card_name:
            attacker_index = i
            attacker = bc
            break
    
    # Find the defender on the opponent's board
    defender_index = None
    defender = None
    for i, bc in enumerate(opponent["board"]):
        if bc["card"]["name"] == target_card_name:
            defender_index = i
            defender = bc
            break
    
    if (attacker is None or 
        defender is None or 
        attacker["card"]["type"] != "Character" or 
        defender["card"]["type"] != "Character" or
        attacker["exerted"] or 
        not attacker["can_act_this_turn"] or
        attacker["card"]["attack"] is None or
        attacker["card"]["attack"] <= 0):
        # Invalid challenge
        return game_state
    
    # Exert the attacker
    attacker["exerted"] = True
    
    # Store attack values before any banishment occurs
    attacker_attack = attacker["card"]["attack"]
    defender_attack = defender["card"]["attack"] if defender["card"]["attack"] is not None else 0
    
    # Apply damage simultaneously to both characters
    attacker["damage"] += defender_attack
    defender["damage"] += attacker_attack
    
    # Track which cards need to be banished
    attacker_banished = False
    defender_banished = False
    
    # Check if defender is banished (damage >= defense)
    if defender["damage"] >= defender["card"]["defense"]:
        defender_banished = True
    
    # Check if attacker is banished (damage >= defense)
    if attacker["damage"] >= attacker["card"]["defense"]:
        attacker_banished = True
    
    # Process banishments (defender first to avoid index issues)
    if defender_banished:
        # Remove the defender from the board
        banished_card = opponent["board"].pop(defender_index)["card"]
        # Add it to the discard pile
        opponent["discard_pile"].append(banished_card)
    
    if attacker_banished:
        # Remove the attacker from the board
        banished_card = player["board"].pop(attacker_index)["card"]
        # Add it to the discard pile
        player["discard_pile"].append(banished_card)
    
    # Add to game log
    game_state["game_log"].append(action)
    
    return game_state
