#!/usr/bin/env python3
"""
Simple AI Agent for Tic-Tac-Toe MCP Game

This script generates JSON-RPC commands for an AI agent to play tic-tac-toe.
It creates a complete script that can be piped to the MCP server.

Usage:
    # Generate a complete game and pipe to MCP server
    python3 scripts/ai_agent_simple.py | GAME_DB_PATH=":memory:" ./target/release/game-mcp-server

    # Generate with verbose output
    python3 scripts/ai_agent_simple.py --verbose | GAME_DB_PATH=":memory:" ./target/release/game-mcp-server
"""

import sys
import json
import random
from typing import List, Tuple


class SimpleAIAgent:
    """
    Simple AI that generates a sequence of moves for tic-tac-toe

    Strategy: Make random valid moves until the game ends
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.request_id = 0
        self.moves = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0), (2, 1), (2, 2),
        ]
        random.shuffle(self.moves)

    def log(self, message: str):
        """Log to stderr (stdout is for JSON-RPC)"""
        if self.verbose:
            print(f"[Agent] {message}", file=sys.stderr)

    def emit_request(self, method: str, params: dict = None):
        """Emit a JSON-RPC request to stdout"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        print(json.dumps(request))

    def generate_game_script(self):
        """
        Generate a complete game script.

        This creates a sequence of moves where the AI takes turns with
        a simulated opponent.
        """
        self.log("Generating AI agent game script...")

        # View initial state
        self.log("Viewing initial game state")
        self.emit_request("view_game_state")

        # Check whose turn it is
        self.log("Checking whose turn it is")
        self.emit_request("get_turn")

        # Make AI's first move (assuming AI goes first as X)
        # In a real game, we'd check the turn first, but for this demo we'll just alternate
        move_count = 0
        max_moves = 9  # Maximum possible moves in tic-tac-toe

        for i, (row, col) in enumerate(self.moves[:max_moves]):
            move_count += 1
            self.log(f"Move {move_count}: AI making move at ({row}, {col})")
            self.emit_request("make_move", {"row": row, "col": col})

            # Occasionally taunt (every 2-3 moves)
            if move_count % 2 == 0:
                taunts = [
                    "Is that the best you can do?",
                    "My neural networks are barely warm!",
                    "Interesting strategy... I guess.",
                    "Calculating victory probability: 99.7%",
                ]
                taunt = random.choice(taunts)
                self.log(f"Sending taunt: {taunt}")
                self.emit_request("taunt_player", {"message": taunt})

            # Check game state every few moves
            if move_count % 2 == 1:
                self.log("Checking game state")
                self.emit_request("view_game_state")

        # Final game state
        self.log("Viewing final game state")
        self.emit_request("view_game_state")

        # Get game history
        self.log("Getting game history")
        self.emit_request("get_game_history")

        self.log(f"Generated {self.request_id} JSON-RPC requests")
        self.log("Script complete!")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Simple AI Agent for Tic-Tac-Toe")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging to stderr")

    args = parser.parse_args()

    agent = SimpleAIAgent(verbose=args.verbose)
    agent.generate_game_script()


if __name__ == "__main__":
    main()
