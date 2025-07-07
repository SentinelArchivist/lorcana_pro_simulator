import pytest
import sys
from unittest.mock import patch, MagicMock
import importlib


class TestMainEntryPoint:
    """Test suite for the main entry point of Lorcana Pro-Simulator."""
    
    def setup_method(self):
        """Setup method that runs before each test."""
        # If the module was already imported, reload it to ensure fresh state
        if 'src.main' in sys.modules:
            importlib.reload(sys.modules['src.main'])

    @patch('src.gui.launch_app')
    def test_default_mode_launches_gui(self, mock_launch_app):
        """Test that the default mode (no args) launches the GUI."""
        # Mock sys.argv to simulate no arguments
        with patch('sys.argv', ['main.py']):
            # Import the main module
            from src.main import main
            # Call the main function directly
            main()
            # Verify that the GUI launch function was called
            mock_launch_app.assert_called_once()

    @patch('src.cli.run_tournament')
    def test_cli_mode_runs_tournament(self, mock_run_tournament):
        """Test that CLI mode runs the tournament with correct arguments."""
        # Mock sys.argv to simulate CLI arguments
        with patch('sys.argv', ['main.py', '--cli', '--decklist', 'path/to/decks', '--output', 'path/to/output']):
            # Import the main module
            from src.main import main
            # Call the main function directly
            main()
            # Verify that the tournament runner was called with correct arguments
            mock_run_tournament.assert_called_once_with('path/to/decks', 'path/to/output')

    def test_cli_mode_missing_decklist_raises_error(self):
        """Test that CLI mode without decklist argument raises an error."""
        # Mock sys.argv to simulate missing decklist argument
        with patch('sys.argv', ['main.py', '--cli', '--output', 'path/to/output']):
            # Import the main module
            from src.main import parse_arguments
            # Calling parse_arguments should raise SystemExit
            with pytest.raises(SystemExit):
                parse_arguments()

    def test_cli_mode_missing_output_raises_error(self):
        """Test that CLI mode without output argument raises an error."""
        # Mock sys.argv to simulate missing output argument
        with patch('sys.argv', ['main.py', '--cli', '--decklist', 'path/to/decks']):
            # Import the main module
            from src.main import parse_arguments
            # Calling parse_arguments should raise SystemExit
            with pytest.raises(SystemExit):
                parse_arguments()
