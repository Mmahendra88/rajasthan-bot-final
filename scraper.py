import requests
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from config import WEBSITES

class WebsiteScraper:
    def __init__(self):
        self.websites = WEBSITES
    
    async def fetch_website_content(self, session, url):
        """Fetch content from a single website"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    
                    # Get text content
                    text = soup.get_text()
                    
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    
                    return {
                        'url': url,
                        'content': text[:2000]  # Limit content length
                    }
                else:
                    return {
                        'url': url,
                        'content': f"Could not fetch content from {url}. Status: {response.status}"
                    }
        except Exception as e:
            return {
                'url': url,
                'content': f"Error fetching {url}: {str(e)}"
            }
    
    async def scrape_all_websites(self):
        """Scrape content from all websites asynchronously"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for website in self.websites:
                task = self.fetch_website_content(session, website)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return results
    
    def get_combined_data(self):
        """Get combined data from all websites"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(self.scrape_all_websites())
        
        combined_data = ""
        for result in results:
            combined_data += f"From {result['url']}:\n{result['content']}\n\n"
        
        return combined_data
