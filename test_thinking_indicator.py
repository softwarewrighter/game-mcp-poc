#!/usr/bin/env python3
"""Test the MCP thinking indicator by triggering an MCP call and capturing it."""

from playwright.sync_api import sync_playwright
import subprocess
import time
import threading

def trigger_mcp_call():
    """Trigger an MCP call after a short delay."""
    time.sleep(1)  # Wait for browser to be ready
    print("Triggering MCP call...")
    subprocess.run([
        "bash", "-c",
        "echo '{\"jsonrpc\": \"2.0\", \"method\": \"view_game_state\", \"params\": {}, \"id\": 99}' | GAME_DB_PATH=game.db ./target/release/game-mcp-server"
    ])
    print("MCP call completed!")

def test_thinking_indicator():
    """Test and screenshot the thinking indicator."""
    with sync_playwright() as p:
        print("Launching Firefox...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()

        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000", timeout=10000)
        time.sleep(2)

        print("\n=== Initial screenshot ===")
        page.screenshot(path="screenshots/before_thinking.png")
        print("Screenshot saved: screenshots/before_thinking.png")

        # Start MCP call in background thread
        mcp_thread = threading.Thread(target=trigger_mcp_call)
        mcp_thread.start()

        # Wait a bit for the MCP call to trigger
        time.sleep(1.5)

        print("\n=== Capturing thinking indicator ===")
        # Check if thinking indicator is visible
        thinking_indicator = page.locator(".mcp-thinking-indicator")
        if thinking_indicator.count() > 0:
            print("✓ Thinking indicator is visible!")
            thinking_text = thinking_indicator.text_content()
            print(f"  Text: {thinking_text}")
        else:
            print("✗ Thinking indicator NOT found")

        page.screenshot(path="screenshots/with_thinking_indicator.png")
        print("Screenshot saved: screenshots/with_thinking_indicator.png")

        # Wait to see it disappear
        print("\n=== Waiting for indicator to disappear (2s delay) ===")
        time.sleep(2.5)

        page.screenshot(path="screenshots/after_thinking.png")
        print("Screenshot saved: screenshots/after_thinking.png")

        if thinking_indicator.count() == 0:
            print("✓ Thinking indicator has disappeared!")
        else:
            print("Note: Indicator may still be visible")

        print("\n=== Keeping browser open for 3 seconds ===")
        time.sleep(3)

        mcp_thread.join()
        browser.close()
        print("Done!")

if __name__ == "__main__":
    test_thinking_indicator()
