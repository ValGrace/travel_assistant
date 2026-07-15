import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Launch a headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Define the Google search URL with operators
        query = 'inurl:.ke intext:"room" hotels Nairobi'
        url = f"https://google.com{query}"
        
        # Navigate and wait for results to load
        await page.goto(url)
        await page.wait_for_selector("div.g")
        
        # Extract search result elements
        results = await page.locator("div.g").all()
        
        for result in results:
            title_el = await result.locator("h3").first()
            link_el = await result.locator("a").first()
            
            title = await title_el.inner_text() if title_el else "No Title"
            link = await link_el.get_attribute("href") if link_el else "No Link"
            
            print(f"Found: {title} -> {link}")
            
        await browser.close()

asyncio.run(main())
