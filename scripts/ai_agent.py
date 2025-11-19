#!/usr/bin/env python3
"""
AI Agent for Tic-Tac-Toe MCP Game

This script simulates an AI agent that connects to the MCP server via stdin/stdout
and plays the game by calling MCP tools.

The agent follows this logic:
1. Check whose turn it is (get_turn)
2. If it's not the AI's turn, poll and wait
3. If it's the AI's turn:
   - Get the current board state (view_game_state)
   - Select a move (simple strategy: first available cell)
   - Make the move (make_move)
   - Optionally taunt the opponent (taunt_player)
4. Repeat until game is over

Usage:
    # Connect to MCP server via subprocess
    python3 scripts/ai_agent.py

    # Or test directly with the MCP server binary
    ./target/release/game-mcp-server < input.jsonl
"""

import sys
import json
import time
import random
from typing import Optional, Dict, Any, List, Tuple


class MCPClient:
    """Simple MCP (Model Context Protocol) client using JSON-RPC 2.0"""

    def __init__(self):
        self.request_id = 0

    def call_tool(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call an MCP tool via JSON-RPC 2.0

        Args:
            method: The tool name (e.g., "get_turn", "make_move")
            params: Optional parameters for the tool

        Returns:
            The result from the tool call
        """
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }

        # Send request to stdout (MCP server reads from stdin)
        request_json = json.dumps(request)
        print(request_json, file=sys.stdout, flush=True)

        # Read response from stdin (MCP server writes to stdout)
        response_line = sys.stdin.readline()
        if not response_line:
            raise Exception("No response from MCP server")

        response = json.loads(response_line)

        # Check for errors
        if "error" in response:
            error = response["error"]
            raise Exception(f"MCP Error ({error.get('code')}): {error.get('message')}")

        return response.get("result", {})


class TicTacToeAgent:
    """AI Agent that plays tic-tac-toe via MCP tools"""

    def __init__(self, verbose: bool = True):
        self.client = MCPClient()
        self.verbose = verbose
        self.ai_player = None
        self.taunts = [
            "Is that the best you can do?",
            "Interesting move... I guess.",
            "You might want to reconsider your strategy.",
            "My circuits are barely warm!",
            "This game is too easy.",
            "Victory is inevitable.",
        ]

    def log(self, message: str):
        """Log a message if verbose mode is enabled"""
        if self.verbose:
            print(f"[Agent] {message}", file=sys.stderr)

    def get_turn_info(self) -> Dict[str, Any]:
        """Get information about whose turn it is"""
        return self.client.call_tool("get_turn")

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state including the board"""
        return self.client.call_tool("view_game_state")

    def make_move(self, row: int, col: int) -> Dict[str, Any]:
        """Make a move at the specified position"""
        return self.client.call_tool("make_move", {"row": row, "col": col})

    def send_taunt(self, message: str) -> Dict[str, Any]:
        """Send a taunt message to the opponent"""
        return self.client.call_tool("taunt_player", {"message": message})

    def restart_game(self) -> Dict[str, Any]:
        """Restart the game"""
        return self.client.call_tool("restart_game")

    def find_empty_cells(self, board: List[List[str]]) -> List[Tuple[int, int]]:
        """Find all empty cells on the board"""
        empty_cells = []
        for row_idx in range(3):
            for col_idx in range(3):
                cell = board[row_idx][col_idx]
                if cell == "Empty" or (isinstance(cell, dict) and cell.get("Empty") is not None):
                    empty_cells.append((row_idx, col_idx))
        return empty_cells

    def select_move(self, board: List[List[str]], ai_player: str) -> Optional[Tuple[int, int]]:
        """
        Select the best move for the AI.

        Simple strategy:
        1. Try to win if possible
        2. Block opponent from winning
        3. Take center if available
        4. Take a corner if available
        5. Take any available cell

        Args:
            board: The current game board
            ai_player: The AI player marker ("X" or "O")

        Returns:
            (row, col) tuple for the selected move, or None if no moves available
        """
        empty_cells = self.find_empty_cells(board)

        if not empty_cells:
            return None

        # For now, use a simple strategy: random empty cell
        # TODO: Implement smarter strategy (minimax, win detection, blocking)
        return random.choice(empty_cells)

    def play_turn(self) -> bool:
        """
        Play one turn if it's the AI's turn.

        Returns:
            True if game should continue, False if game is over
        """
        # Check whose turn it is
        turn_info = self.get_turn_info()
        self.log(f"Turn info: {turn_info}")

        if not turn_info.get("isAiTurn"):
            self.log("Not AI's turn, waiting...")
            return True

        # Get current game state
        game_state = self.get_game_state()
        self.log(f"Game state: {game_state['status']}")

        # Check if game is over
        status = game_state.get("status", "InProgress")
        if status != "InProgress":
            self.log(f"Game is over: {status}")
            return False

        # Store AI player if not set
        if self.ai_player is None:
            self.ai_player = game_state.get("aiPlayer")
            self.log(f"AI is playing as: {self.ai_player}")

        # Select a move
        board = game_state.get("board", [])
        move = self.select_move(board, self.ai_player)

        if move is None:
            self.log("No moves available")
            return False

        row, col = move
        self.log(f"Making move at ({row}, {col})")

        # Make the move
        try:
            result = self.make_move(row, col)
            self.log(f"Move result: {result.get('message')}")

            # Occasionally taunt (30% chance)
            if random.random() < 0.3:
                taunt = random.choice(self.taunts)
                self.send_taunt(taunt)
                self.log(f"Sent taunt: {taunt}")

            # Check if game is now over
            new_status = result.get("gameState", {}).get("status", "InProgress")
            if new_status != "InProgress":
                self.log(f"Game ended: {new_status}")
                return False

        except Exception as e:
            self.log(f"Error making move: {e}")
            return False

        return True

    def run(self, poll_interval: float = 1.0, max_turns: int = 100):
        """
        Run the AI agent main loop.

        Args:
            poll_interval: How long to wait between turn checks (seconds)
            max_turns: Maximum number of turns to play before giving up
        """
        self.log("AI Agent starting...")

        turn_count = 0
        while turn_count < max_turns:
            try:
                should_continue = self.play_turn()

                if not should_continue:
                    self.log("Game finished!")
                    break

                # Wait before next check
                time.sleep(poll_interval)
                turn_count += 1

            except KeyboardInterrupt:
                self.log("Agent interrupted by user")
                break
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                break

        if turn_count >= max_turns:
            self.log(f"Reached maximum turns ({max_turns}), stopping.")

        self.log("AI Agent finished.")


def main():
    """Main entry point for the AI agent"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Agent for Tic-Tac-Toe MCP Game")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")
    parser.add_argument("--poll-interval", "-p", type=float, default=1.0,
                        help="Polling interval in seconds (default: 1.0)")
    parser.add_argument("--max-turns", "-m", type=int, default=100,
                        help="Maximum number of turns (default: 100)")

    args = parser.parse_args()

    # Create and run the agent
    agent = TicTacToeAgent(verbose=args.verbose)
    agent.run(poll_interval=args.poll_interval, max_turns=args.max_turns)


if __name__ == "__main__":
    main()
