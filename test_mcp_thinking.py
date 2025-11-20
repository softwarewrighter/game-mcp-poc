#!/usr/bin/env python3
"""Test the MCP thinking indicator using HTTP MCP endpoint."""

from playwright.sync_api import sync_playwright
import requests
import time
import json

def trigger_mcp_call():
    """Trigger an MCP call via HTTP endpoint."""
    print("Triggering MCP call via HTTP...")
    response = requests.post(
        "http://localhost:3000/mcp",
        json={
            "jsonrpc": "2.0",
            "method": "view_game_state",
            "params": {},
            "id": 99
        }
    )
    print(f"MCP call completed! Status: {response.status_code}")
    print(f"Response: {response.json()}")

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
        page.screenshot(path="screenshots/before_mcp_thinking.png")
        print("Screenshot saved: screenshots/before_mcp_thinking.png")

        # Trigger MCP call
        trigger_mcp_call()

        # Wait a moment for SSE to propagate
        time.sleep(0.5)

        print("\n=== Capturing thinking indicator ===")
        # Check if thinking indicator is visible
        thinking_indicator = page.locator(".mcp-thinking-indicator")
        if thinking_indicator.count() > 0:
            print("✓ Thinking indicator is visible!")
            thinking_text = thinking_indicator.text_content()
            print(f"  Text: {thinking_text}")
        else:
            print("✗ Thinking indicator NOT found")

        page.screenshot(path="screenshots/with_mcp_thinking_indicator.png")
        print("Screenshot saved: screenshots/with_mcp_thinking_indicator.png")

        # Wait for it to disappear (2000ms delay + buffer)
        print("\n=== Waiting for indicator to disappear (2.5s delay) ===")
        time.sleep(2.5)

        page.screenshot(path="screenshots/after_mcp_thinking.png")
        print("Screenshot saved: screenshots/after_mcp_thinking.png")

        if thinking_indicator.count() == 0:
            print("✓ Thinking indicator has disappeared!")
        else:
            print("Note: Indicator may still be visible")

        print("\n=== Keeping browser open for 3 seconds ===")
        time.sleep(3)

        browser.close()
        print("Done!")

if __name__ == "__main__":
    test_thinking_indicator()
