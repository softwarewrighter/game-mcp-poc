#!/usr/bin/env python3
"""Take a screenshot of the UI to see the drag-and-drop interface."""

from playwright.sync_api import sync_playwright
import time

def screenshot_ui():
    """Take a screenshot of the current UI state."""
    with sync_playwright() as p:
        print("Launching Firefox...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()

        print("Navigating to http://localhost:3000...")
        page.goto("http://localhost:3000", timeout=10000)

        # Wait for page to load
        time.sleep(3)

        print("\n=== Taking screenshot ===")
        page.screenshot(path="screenshots/ui_with_dragdrop.png", full_page=True)
        print("Screenshot saved to: screenshots/ui_with_dragdrop.png")

        # Check for draggable mark
        draggable_mark = page.locator(".draggable-mark")
        if draggable_mark.count() > 0:
            print(f"\n✓ Draggable mark found!")
            mark_text = draggable_mark.text_content()
            print(f"  Mark shows: {mark_text}")

            # Check if enabled or disabled
            mark_class = draggable_mark.get_attribute("class")
            if "enabled" in mark_class:
                print("  Status: ENABLED (pulsing/glowing)")
            else:
                print("  Status: DISABLED (waiting for turn)")

        # Check for drag hint
        drag_hint = page.locator(".drag-hint")
        if drag_hint.count() > 0:
            hint_text = drag_hint.text_content()
            print(f"\n✓ Drag hint: {hint_text}")

        # Count drop targets
        drop_targets = page.locator(".drop-target").count()
        print(f"\n✓ Found {drop_targets} drop target cells")

        # Check latest taunt
        taunts = page.locator(".taunt-message")
        if taunts.count() > 0:
            latest_taunt = taunts.last.text_content()
            print(f"\n✓ Latest taunt: {latest_taunt}")

        print("\n=== Keeping browser open for 5 seconds ===")
        time.sleep(5)

        browser.close()
        print("Done!")

if __name__ == "__main__":
    screenshot_ui()
