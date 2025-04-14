import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BUILD_SCRIPT = Path("gui_agents/s2/utils/build_dom_tree.js")  # adjust path as needed

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        browser_context = await browser.new_context()
        
        # 1) Inject the build_dom_tree logic before any CSP kicks in
        await browser_context.add_init_script(BUILD_SCRIPT.read_text())
        page = await browser_context.new_page()

        # 2) Navigate to your page under test
        await page.goto("https://www.google.com")

        # 3) Retrieve clickable elements (with highlighting)
        result = await page.evaluate("""() => 
            window.get_clickable_elements(true, ['id','class','name'])
        """)

        # result is a dict: { 'element_str': str, 'selector_map': { idx: {...} } }
        print("=== Clickable Elements ===")
        print(result["element_str"])

        # 4) Click the 2nd highlighted element (index = 1)
        idx_to_click = 1
        handle = await page.evaluate_handle(f"window.get_highlight_element({idx_to_click})")
        element = handle.as_element()
        if element:
            await element.click()
        else:
            print(f"No element found at highlight index {idx_to_click}")

        # 5) Remove highlights
        await page.wait_for_event('load')
        await page.evaluate("""() => 
            window.get_clickable_elements(true, ['id','class','name'])
        """)
        await page.evaluate_handle(f"window.get_highlight_element({idx_to_click})")
        await page.evaluate("window.remove_highlight()")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
