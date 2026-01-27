"""
Browse Tool - Playwright Browser Automation
Uses Playwright to navigate and retrieve page content
"""
import asyncio
from playwright.async_api import async_playwright, Browser, Page
from typing import Optional, Tuple
import random
import config


class BrowserTool:
    """
    Browser automation tool using Playwright
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        
    async def init_browser(self) -> None:
        """Initialize the browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=config.BROWSER_HEADLESS,
            slow_mo=config.BROWSER_SLOW_MO if hasattr(config, 'BROWSER_SLOW_MO') else 0
        )
        mode = "VISIBLE" if not config.BROWSER_HEADLESS else "HEADLESS"
        print(f"Browser initialized ({mode} MODE)")
        
    async def close_browser(self) -> None:
        """Close the browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("Browser closed")
        
    async def browse_page(self, url: str) -> Tuple[str, str]:
        """
        Navigate to a URL and retrieve the page content
        
        Args:
            url: The URL to navigate to
            
        Returns:
            Tuple of (HTML content, page title)
        """
        if not self.browser:
            await self.init_browser()
            
        context = await self.browser.new_context(
            extra_http_headers=config.REQUEST_HEADERS,
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Navigate with timeout
            await page.goto(url, timeout=config.BROWSER_TIMEOUT, wait_until="domcontentloaded")
            
            # Wait for content to load
            await page.wait_for_timeout(1000)
            
            # VISIBLE SCROLLING: Scroll down slowly to load dynamic content
            for i in range(3):
                await page.evaluate(f"window.scrollTo(0, {(i + 1) * 600})")
                await page.wait_for_timeout(400)  # Pause to see scroll
            
            # Scroll back to top
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(300)
            
            # Get page content
            html_content = await page.content()
            title = await page.title()
            
            return html_content, title
            
        except Exception as e:
            print(f"Browse error for {url}: {e}")
            return "", ""
            
        finally:
            await context.close()
            
    async def browse_multiple(self, urls: list) -> list:
        """
        Browse multiple URLs and return their content
        
        Args:
            urls: List of URLs to browse
            
        Returns:
            List of tuples (url, html_content, title)
        """
        results = []
        
        for url in urls:
            print(f"Browsing: {url}")
            html, title = await self.browse_page(url)
            if html:
                results.append({
                    "url": url,
                    "html": html,
                    "title": title
                })
            # Small delay between requests
            await asyncio.sleep(1)
            
        return results


# Synchronous wrapper functions for easier use
def browse_url(url: str) -> Tuple[str, str]:
    """
    Synchronous wrapper to browse a single URL
    
    Args:
        url: URL to browse
        
    Returns:
        Tuple of (HTML content, page title)
    """
    async def _browse():
        tool = BrowserTool()
        try:
            await tool.init_browser()
            return await tool.browse_page(url)
        finally:
            await tool.close_browser()
            
    return asyncio.run(_browse())


def browse_urls(urls: list) -> list:
    """
    Synchronous wrapper to browse multiple URLs
    
    Args:
        urls: List of URLs to browse
        
    Returns:
        List of browse results
    """
    async def _browse_all():
        tool = BrowserTool()
        try:
            await tool.init_browser()
            return await tool.browse_multiple(urls)
        finally:
            await tool.close_browser()
            
    return asyncio.run(_browse_all())


if __name__ == "__main__":
    # Test browsing
    test_url = "https://www.hepsiemlak.com"
    print(f"Testing browse for: {test_url}")
    html, title = browse_url(test_url)
    print(f"Title: {title}")
    print(f"HTML length: {len(html)} characters")
