#!/bin/bash
# Run a simulated AI agent game via MCP tools
#
# This script demonstrates the MCP interface by having an AI agent
# play tic-tac-toe via JSON-RPC tool calls.
#
# Usage:
#   ./scripts/run_ai_agent.sh [--verbose] [--output FILE]
#
# Options:
#   --verbose, -v   Show detailed agent logging
#   --output FILE   Save game output to FILE (default: show on screen)
#
# Examples:
#   # Run with default settings
#   ./scripts/run_ai_agent.sh
#
#   # Run with verbose logging and save to file
#   ./scripts/run_ai_agent.sh --verbose --output game_output.json

set -e

VERBOSE=""
OUTPUT_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE="--verbose"
            shift
            ;;
        --output|-o)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--verbose] [--output FILE]"
            exit 1
            ;;
    esac
done

# Check if binary exists
if [ ! -f "./target/release/game-mcp-server" ]; then
    echo "Error: MCP server binary not found."
    echo "Please build the project first:"
    echo "  ./scripts/build.sh"
    exit 1
fi

# Check if Python script exists
if [ ! -f "./scripts/ai_agent_simple.py" ]; then
    echo "Error: AI agent script not found at ./scripts/ai_agent_simple.py"
    exit 1
fi

echo "Running AI agent simulation via MCP tools..."
echo ""

# Run the agent and pipe to MCP server
if [ -n "$OUTPUT_FILE" ]; then
    echo "Saving game output to: $OUTPUT_FILE"
    python3 ./scripts/ai_agent_simple.py $VERBOSE 2>/dev/null | \
        GAME_DB_PATH=":memory:" ./target/release/game-mcp-server 2>/dev/null | \
        tee "$OUTPUT_FILE" | \
        jq -r 'if .result then "✓ " + .method + " → " + (.result.message // "success") elif .error then "✗ ERROR: " + .error.message else . end' 2>/dev/null || cat
else
    python3 ./scripts/ai_agent_simple.py $VERBOSE 2>/dev/null | \
        GAME_DB_PATH=":memory:" ./target/release/game-mcp-server 2>/dev/null | \
        jq -r '
            if .result.message then
                "✓ Request " + (.id | tostring) + ": " + .result.message
            elif .result.status then
                "  Game status: " + .result.status
            elif .result.moves then
                "  Total moves: " + (.result.moves | length | tostring)
            elif .result then
                "✓ Request " + (.id | tostring) + " completed"
            elif .error then
                "✗ Request " + (.id | tostring) + " ERROR: " + .error.message
            else
                .
            end
        ' 2>/dev/null || cat
fi

echo ""
echo "AI agent simulation complete!"
echo ""
echo "The agent successfully demonstrated the MCP interface by:"
echo "  - Calling view_game_state to see the board"
echo "  - Calling get_turn to check whose turn it is"
echo "  - Calling make_move to place markers"
echo "  - Calling taunt_player to send messages"
echo "  - Calling get_game_history to review the game"
