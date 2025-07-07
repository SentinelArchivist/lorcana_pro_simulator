"""
Results Analyzer module for Lorcana Pro Simulator.

This module provides functionality to analyze tournament results and generate CSV reports.
"""

import csv
from typing import Dict, List, Any, Tuple
from collections import Counter


def generate_summary_report(summary_data: Dict[str, Dict[str, Any]], output_filepath: str) -> None:
    """
    Generate a CSV report summarizing tournament results.
    
    Args:
        summary_data: Dictionary of win statistics for each deck
                     (e.g., {"Deck A": {"wins": 55, "losses": 45, "win_rate": 0.55}})
        output_filepath: Path where the CSV file will be saved
    """
    with open(output_filepath, 'w', newline='') as csvfile:
        fieldnames = ['Deck Name', 'Win Rate', 'Wins', 'Losses']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for deck_name, stats in summary_data.items():
            writer.writerow({
                'Deck Name': deck_name,
                'Win Rate': f"{stats.get('win_rate', 0):.4f}",
                'Wins': stats.get('wins', 0),
                'Losses': stats.get('losses', 0)
            })


def generate_optimal_plays_report(all_game_logs: List[Dict], summary_data: Dict[str, Dict[str, Any]], 
                                 output_filepath: str, max_turns: int = 10) -> None:
    """
    Generate a CSV report of optimal play sequences for top-performing decks.
    
    Args:
        all_game_logs: List of game logs, each containing a list of player actions
        summary_data: Dictionary of win statistics for each deck
        output_filepath: Path where the CSV file will be saved
        max_turns: Maximum number of turns to analyze (default: 10)
    """
    # Identify top-performing deck(s)
    top_decks = _identify_top_decks(summary_data)
    
    # Filter game logs to only include games where a top deck won
    winning_logs = _filter_winning_logs(all_game_logs, top_decks)
    
    # Extract action sequences for the first max_turns turns
    action_sequences = _extract_action_sequences(winning_logs, max_turns)
    
    # Find most frequent actions for each matchup and turn
    optimal_actions = _find_most_frequent_actions(action_sequences)
    
    # Write results to CSV
    _write_optimal_actions_to_csv(optimal_actions, output_filepath)


def _identify_top_decks(summary_data: Dict[str, Dict[str, Any]]) -> List[str]:
    """
    Identify the top-performing deck(s) based on win rate.
    
    Args:
        summary_data: Dictionary of win statistics for each deck
        
    Returns:
        List of top deck names
    """
    if not summary_data:
        return []
    
    # Find the highest win rate
    max_win_rate = max(data.get('win_rate', 0) for data in summary_data.values())
    
    # Return all decks with the highest win rate
    return [deck_name for deck_name, data in summary_data.items() 
            if data.get('win_rate', 0) == max_win_rate]


def _filter_winning_logs(all_game_logs: List[Dict], top_decks: List[str]) -> List[Tuple[str, str, Dict]]:
    """
    Filter game logs to only include games won by top decks.
    
    Args:
        all_game_logs: List of all game logs
        top_decks: List of top performing deck names
        
    Returns:
        List of tuples containing (winning_deck, opponent_deck, game_log)
    """
    winning_logs = []
    
    for game_log in all_game_logs:
        # Skip incomplete game logs
        if not game_log or "winner" not in game_log:
            continue
            
        winner = game_log.get("winner")
        deck1_name = game_log.get("deck1_name")
        deck2_name = game_log.get("deck2_name")
        
        # Determine the winning deck
        winning_deck = None
        opponent_deck = None
        
        if winner == "Player1":
            winning_deck = deck1_name
            opponent_deck = deck2_name
        elif winner == "Player2":
            winning_deck = deck2_name
            opponent_deck = deck1_name
        
        # Only include games won by top decks
        if winning_deck in top_decks:
            # Pass the entire game_log dictionary, not just the game_log field
            winning_logs.append((winning_deck, opponent_deck, game_log))
    
    return winning_logs


def _extract_action_sequences(winning_logs: List[Tuple[str, str, Dict]], max_turns: int) -> Dict:
    """
    Extract action sequences for the first max_turns turns.
    
    Args:
        winning_logs: List of tuples containing (winning_deck, opponent_deck, game_log)
        max_turns: Maximum number of turns to analyze
        
    Returns:
        Dictionary mapping (winning_deck, opponent_deck, turn) to a list of actions
    """
    action_sequences = {}
    
    for winning_deck, opponent_deck, game_data in winning_logs:
        matchup = (winning_deck, opponent_deck)
        
        # Initialize the matchup in the dictionary if not present
        if matchup not in action_sequences:
            action_sequences[matchup] = {turn: [] for turn in range(1, max_turns + 1)}
        
        # In the test data, the game_data contains metadata at the top level
        # and the actual game log is in the 'game_log' field
        if not isinstance(game_data, dict) or "game_log" not in game_data:
            continue
            
        # Get the metadata and game log
        deck1_name = game_data.get("deck1_name")
        deck2_name = game_data.get("deck2_name")
        winner = game_data.get("winner")
        game_log = game_data.get("game_log", [])
        
        # Determine the winning player index based on the winner and deck names
        winning_player_index = None
        if winner == "Player1" and deck1_name == winning_deck:
            winning_player_index = 0  # Player1 is index 0
        elif winner == "Player2" and deck2_name == winning_deck:
            winning_player_index = 1  # Player2 is index 1
        else:
            # If we can't determine the winning player index based on winner field,
            # use a more general approach by comparing the winning deck name with deck names
            if winning_deck == deck1_name:
                winning_player_index = 0
            elif winning_deck == deck2_name:
                winning_player_index = 1
        
        # If we still can't determine the winning player index, skip this game
        if winning_player_index is None:
            continue
        
        # Extract actions for each turn
        current_turn = 1
        for action in game_log:
            if current_turn > max_turns:
                break
                
            # Only add actions from the winning player and for the current turn
            player_index = action.get("player_index")
            if player_index == winning_player_index:
                action_sequences[matchup][current_turn].append(action)
            
            # Check if this action ends the turn
            if action.get("action_type") == "PASS_TURN":
                current_turn += 1
    
    return action_sequences


def _find_most_frequent_actions(action_sequences: Dict) -> List[Dict]:
    """
    Find the most frequent actions for each matchup and turn.
    
    Args:
        action_sequences: Dictionary mapping (winning_deck, opponent_deck, turn) to a list of actions
        
    Returns:
        List of dictionaries containing most frequent actions
    """
    optimal_actions = []
    
    for (winning_deck, opponent_deck), turns in action_sequences.items():
        for turn, actions in turns.items():
            if not actions:
                continue
                
            # Count action types
            action_types = Counter([action.get("action_type") for action in actions if action.get("action_type")])
            if not action_types:
                continue
                
            most_common_action_type = action_types.most_common(1)[0][0]
            
            # Count source cards
            source_cards = Counter([action.get("source_card") for action in actions 
                                   if action.get("action_type") == most_common_action_type 
                                   and action.get("source_card")])
            most_common_source = source_cards.most_common(1)[0][0] if source_cards else None
            
            # Count target cards
            target_cards = Counter([action.get("target_card") for action in actions 
                                   if action.get("action_type") == most_common_action_type 
                                   and action.get("source_card") == most_common_source 
                                   and action.get("target_card")])
            most_common_target = target_cards.most_common(1)[0][0] if target_cards else None
            
            optimal_actions.append({
                "Winning Deck": winning_deck,
                "Opponent Deck": opponent_deck,
                "Turn": turn,
                "Most Frequent Action Type": most_common_action_type,
                "Most Frequent Source Card": most_common_source,
                "Most Frequent Target Card": most_common_target
            })
    
    return optimal_actions


def _write_optimal_actions_to_csv(optimal_actions: List[Dict], output_filepath: str) -> None:
    """
    Write optimal actions to a CSV file.
    
    Args:
        optimal_actions: List of dictionaries containing most frequent actions
        output_filepath: Path where the CSV file will be saved
    """
    if not optimal_actions:
        # Create an empty CSV with headers if no actions
        with open(output_filepath, 'w', newline='') as csvfile:
            fieldnames = ['Winning Deck', 'Opponent Deck', 'Turn', 
                         'Most Frequent Action Type', 'Most Frequent Source Card', 'Most Frequent Target Card']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        return
    
    with open(output_filepath, 'w', newline='') as csvfile:
        fieldnames = ['Winning Deck', 'Opponent Deck', 'Turn', 
                     'Most Frequent Action Type', 'Most Frequent Source Card', 'Most Frequent Target Card']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for action in optimal_actions:
            writer.writerow(action)
