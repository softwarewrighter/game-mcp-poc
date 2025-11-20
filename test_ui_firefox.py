#!/usr/bin/env python3
"""Test the Tic-Tac-Toe UI at localhost:3000 using Firefox with Playwright."""

from playwright.sync_api import sync_playwright, expect
import time

def test_ui():
    """Test the UI loads and basic interactions work."""
    with sync_playwright() as p:
        print("Launching Firefox...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()

        print("Navigating to http://localhost:3000...")
        try:
            page.goto("http://localhost:3000", timeout=10000)
        except Exception as e:
            print(f"Navigation warning: {e}")
            # Continue anyway

        # Wait for page to load (use domcontentloaded instead of networkidle)
        try:
            page.wait_for_load_state("domcontentloaded", timeout=5000)
        except Exception as e:
            print(f"Load state warning: {e}")

        time.sleep(3)  # Give WASM time to initialize

        print("\n=== Taking screenshot of initial page ===")
        page.screenshot(path="screenshots/ui_initial.png")
        print("Screenshot saved to: screenshots/ui_initial.png")

        # Check page title
        title = page.title()
        print(f"\nPage title: {title}")

        # Get page content to verify elements loaded
        print("\n=== Checking page elements ===")

        # Look for the game board
        board_cells = page.locator(".cell").count()
        print(f"Found {board_cells} board cells")

        # Look for game status
        status_text = page.locator(".game-status").text_content() if page.locator(".game-status").count() > 0 else "Not found"
        print(f"Game status: {status_text}")

        # Look for trash talk panel
        trash_talk_panel = page.locator(".trash-talk-panel").count()
        print(f"Trash talk panel present: {trash_talk_panel > 0}")

        # Test clicking a cell if board exists
        if board_cells >= 9:
            print("\n=== Testing cell click ===")
            first_cell = page.locator(".cell").first
            first_cell.click()
            time.sleep(1)

            page.screenshot(path="screenshots/ui_after_move.png")
            print("Screenshot after move saved to: screenshots/ui_after_move.png")

            # Check if cell was marked
            cell_content = first_cell.text_content()
            print(f"Cell content after click: {cell_content}")

        # Test trash talk input if present
        trash_input = page.locator("input[type='text'], textarea").first
        if trash_input.count() > 0:
            print("\n=== Testing trash talk input ===")
            trash_input.fill("Nice move... NOT!")
            time.sleep(1)

            # Look for submit button
            submit_btn = page.locator("button").filter(has_text="Send")
            if submit_btn.count() > 0:
                submit_btn.click()
                time.sleep(1)
                print("Trash talk submitted")

                page.screenshot(path="screenshots/ui_with_taunt.png")
                print("Screenshot with taunt saved to: screenshots/ui_with_taunt.png")

        # Check console for errors
        print("\n=== Checking browser console ===")
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        # Wait a bit to collect any console messages
        time.sleep(2)

        if console_messages:
            print("Console messages:")
            for msg in console_messages[-10:]:  # Show last 10 messages
                print(f"  {msg}")

        # Final screenshot
        print("\n=== Taking final screenshot ===")
        page.screenshot(path="screenshots/ui_final.png", full_page=True)
        print("Full page screenshot saved to: screenshots/ui_final.png")

        print("\n=== Test complete! Keeping browser open for 10 seconds ===")
        time.sleep(10)

        browser.close()
        print("\nBrowser closed.")

if __name__ == "__main__":
    test_ui()
