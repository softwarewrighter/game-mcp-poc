
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:1461")
        await page.screenshot(path="playwright_screenshot.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
