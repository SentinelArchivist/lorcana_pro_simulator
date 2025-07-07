#!/usr/bin/env python3
"""
Main entry point for the Lorcana Pro-Simulator.
Parses command-line arguments and launches the appropriate application mode (GUI or CLI).
"""

import argparse
import sys


def parse_arguments():
    """Parse command line arguments for the application."""
    parser = argparse.ArgumentParser(
        description="Lorcana Pro-Simulator - A professional-grade simulator for Lorcana card game"
    )
    
    # Add CLI mode flag
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in command-line interface mode (requires --decklist and --output)"
    )
    
    # Add decklist argument for CLI mode
    parser.add_argument(
        "--decklist",
        type=str,
        help="Path to the decklist file or directory (required in CLI mode)"
    )
    
    # Add output argument for CLI mode
    parser.add_argument(
        "--output",
        type=str,
        help="Path to save the output results (required in CLI mode)"
    )
    
    args = parser.parse_args()
    
    # Validate that CLI mode has required arguments
    if args.cli and (args.decklist is None or args.output is None):
        parser.error("CLI mode requires both --decklist and --output arguments")
    
    return args


def main():
    """Main function to launch the appropriate application mode."""
    args = parse_arguments()
    
    if args.cli:
        # CLI mode - import necessary modules and orchestrate the flow
        from src.cli import run_tournament
        run_tournament(args.decklist, args.output)
    else:
        # Default GUI mode
        from src.gui import launch_app
        launch_app()


if __name__ == "__main__":
    main()
