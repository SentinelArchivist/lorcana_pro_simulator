"""
Tests for the Results Analyzer module.

This module tests the functionality to analyze tournament results and generate CSV reports.
"""

import unittest
import os
import io
import csv
import tempfile
from typing import Dict, List, Any

from src.results_analyzer import (
    generate_summary_report,
    generate_optimal_plays_report,
    _identify_top_decks,
    _filter_winning_logs,
    _extract_action_sequences,
    _find_most_frequent_actions
)


class TestResultsAnalyzer(unittest.TestCase):
    """Test cases for the Results Analyzer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Sample summary data
        self.sample_summary_data = {
            "Deck A": {"wins": 55, "losses": 45, "win_rate": 0.55},
            "Deck B": {"wins": 40, "losses": 60, "win_rate": 0.40},
            "Deck C": {"wins": 60, "losses": 40, "win_rate": 0.60}
        }
        
        # Sample game logs
        self.sample_game_logs = [
            {
                "deck1_name": "Deck C",
                "deck2_name": "Deck A",
                "winner": "Player1",
                "game_log": [
                    {"action_type": "INK_CARD", "source_card": "Card C1", "target_card": None, "player_index": 0},
                    {"action_type": "INK_CARD", "source_card": "Card A1", "target_card": None, "player_index": 1},
                    {"action_type": "PLAY_CARD", "source_card": "Card C2", "target_card": None, "player_index": 0},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 0},
                    {"action_type": "PLAY_CARD", "source_card": "Card A2", "target_card": None, "player_index": 1},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 1},
                    {"action_type": "QUEST", "source_card": "Card C2", "target_card": None, "player_index": 0},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 0}
                ]
            },
            {
                "deck1_name": "Deck C",
                "deck2_name": "Deck B",
                "winner": "Player1",
                "game_log": [
                    {"action_type": "INK_CARD", "source_card": "Card C1", "target_card": None, "player_index": 0},
                    {"action_type": "INK_CARD", "source_card": "Card B1", "target_card": None, "player_index": 1},
                    {"action_type": "PLAY_CARD", "source_card": "Card C2", "target_card": None, "player_index": 0},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 0},
                    {"action_type": "PLAY_CARD", "source_card": "Card B2", "target_card": None, "player_index": 1},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 1},
                    {"action_type": "CHALLENGE", "source_card": "Card C2", "target_card": "Card B2", "player_index": 0},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 0}
                ]
            },
            {
                "deck1_name": "Deck A",
                "deck2_name": "Deck B",
                "winner": "Player2",
                "game_log": [
                    {"action_type": "INK_CARD", "source_card": "Card A1", "target_card": None, "player_index": 0},
                    {"action_type": "INK_CARD", "source_card": "Card B1", "target_card": None, "player_index": 1},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 0},
                    {"action_type": "PLAY_CARD", "source_card": "Card B2", "target_card": None, "player_index": 1},
                    {"action_type": "PASS_TURN", "source_card": None, "target_card": None, "player_index": 1}
                ]
            }
        ]
    
    def test_identify_top_decks(self):
        """Test that top decks are correctly identified."""
        top_decks = _identify_top_decks(self.sample_summary_data)
        self.assertEqual(top_decks, ["Deck C"])
        
        # Test with tied win rates
        tied_data = {
            "Deck A": {"wins": 50, "losses": 50, "win_rate": 0.50},
            "Deck B": {"wins": 50, "losses": 50, "win_rate": 0.50}
        }
        top_tied_decks = _identify_top_decks(tied_data)
        self.assertEqual(set(top_tied_decks), {"Deck A", "Deck B"})
        
        # Test with empty data
        empty_top_decks = _identify_top_decks({})
        self.assertEqual(empty_top_decks, [])
    
    def test_filter_winning_logs(self):
        """Test that game logs are correctly filtered for winning decks."""
        top_decks = ["Deck C"]
        winning_logs = _filter_winning_logs(self.sample_game_logs, top_decks)
        
        # Should return 2 logs where Deck C won
        self.assertEqual(len(winning_logs), 2)
        
        # Check that the winning deck is correctly identified
        for winning_deck, opponent_deck, _ in winning_logs:
            self.assertEqual(winning_deck, "Deck C")
            self.assertIn(opponent_deck, ["Deck A", "Deck B"])
    
    def test_extract_action_sequences(self):
        """Test that action sequences are correctly extracted."""
        top_decks = ["Deck C"]
        winning_logs = _filter_winning_logs(self.sample_game_logs, top_decks)
        action_sequences = _extract_action_sequences(winning_logs, max_turns=2)
        
        # Check that we have entries for both matchups
        self.assertEqual(len(action_sequences), 2)
        
        # Check that each matchup has 2 turns
        for matchup, turns in action_sequences.items():
            self.assertEqual(len(turns), 2)
            
            # Check that turn 1 has actions
            self.assertTrue(len(turns[1]) > 0)
            
            # Check that the actions are from the winning player
            for action in turns[1]:
                self.assertEqual(action["player_index"], 0)  # Deck C is player 0 in both logs
    
    def test_find_most_frequent_actions(self):
        """Test that most frequent actions are correctly identified."""
        top_decks = ["Deck C"]
        winning_logs = _filter_winning_logs(self.sample_game_logs, top_decks)
        action_sequences = _extract_action_sequences(winning_logs, max_turns=2)
        optimal_actions = _find_most_frequent_actions(action_sequences)
        
        # Check that we have entries for actions
        self.assertTrue(len(optimal_actions) > 0)
        
        # Check that the first turn action for Deck C vs Deck A is INK_CARD with Card C1
        deck_c_vs_a_turn1 = next((a for a in optimal_actions 
                                 if a["Winning Deck"] == "Deck C" 
                                 and a["Opponent Deck"] == "Deck A" 
                                 and a["Turn"] == 1), None)
        
        self.assertIsNotNone(deck_c_vs_a_turn1)
        self.assertEqual(deck_c_vs_a_turn1["Most Frequent Action Type"], "INK_CARD")
        self.assertEqual(deck_c_vs_a_turn1["Most Frequent Source Card"], "Card C1")
    
    def test_generate_summary_report(self):
        """Test that summary report is correctly generated."""
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_file:
            temp_filepath = temp_file.name
        
        try:
            # Generate report to temporary file
            generate_summary_report(self.sample_summary_data, temp_filepath)
            
            # Read CSV content
            with open(temp_filepath, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            # Check that we have 3 rows (one for each deck)
            self.assertEqual(len(rows), 3)
            
            # Check that Deck C has the highest win rate
            deck_c_row = next(row for row in rows if row["Deck Name"] == "Deck C")
            self.assertEqual(deck_c_row["Win Rate"], "0.6000")
            self.assertEqual(deck_c_row["Wins"], "60")
            self.assertEqual(deck_c_row["Losses"], "40")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)
    
    def test_generate_optimal_plays_report(self):
        """Test that optimal plays report is correctly generated."""
        # Create a temporary file for the output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as temp_file:
            temp_filepath = temp_file.name
        
        try:
            # Generate report to temporary file
            generate_optimal_plays_report(self.sample_game_logs, self.sample_summary_data, temp_filepath)
            
            # Read CSV content
            with open(temp_filepath, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
            
            # Check that we have rows for Deck C's winning games
            self.assertTrue(len(rows) > 0)
            
            # Check that all rows are for Deck C (the top deck)
            for row in rows:
                self.assertEqual(row["Winning Deck"], "Deck C")
                
            # Check that we have entries for both matchups
            opponent_decks = {row["Opponent Deck"] for row in rows}
            self.assertEqual(opponent_decks, {"Deck A", "Deck B"})
            
            # Check that turn 1 action for Deck C vs Deck A is INK_CARD with Card C1
            deck_c_vs_a_turn1 = next((r for r in rows 
                                    if r["Winning Deck"] == "Deck C" 
                                    and r["Opponent Deck"] == "Deck A" 
                                    and r["Turn"] == "1"), None)
            
            self.assertIsNotNone(deck_c_vs_a_turn1)
            self.assertEqual(deck_c_vs_a_turn1["Most Frequent Action Type"], "INK_CARD")
            self.assertEqual(deck_c_vs_a_turn1["Most Frequent Source Card"], "Card C1")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_filepath):
                os.unlink(temp_filepath)


if __name__ == '__main__':
    unittest.main()
