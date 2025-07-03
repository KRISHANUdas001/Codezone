"""
Base scraper class with common functionality
"""
import time
import random
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime
import json

from config import SCRAPING_CONFIG, REVIEW_SCHEMA

class BaseScraper:
    """Base class for all review scrapers"""
    
    def __init__(self, headless: bool = True, use_proxy: bool = False):
        self.headless = headless
        self.use_proxy = use_proxy
        self.session = requests.Session()
        self.ua = UserAgent()
        self.driver = None
        self.reviews_data = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={self.ua.random}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            self.logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def make_request(self, url: str, headers: Optional[Dict] = None) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        if not headers:
            headers = {'User-Agent': self.ua.random}
        
        for attempt in range(SCRAPING_CONFIG['max_retries']):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=SCRAPING_CONFIG['timeout']
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                self.logger.warning(f"Request attempt {attempt + 1} failed for {url}: {e}")
                if attempt < SCRAPING_CONFIG['max_retries'] - 1:
                    time.sleep(random.uniform(1, 3))
                else:
                    self.logger.error(f"All request attempts failed for {url}")
                    return None
    
    def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element to be present"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return True
        except TimeoutException:
            return False
    
    def extract_text(self, element, selector: str) -> str:
        """Safely extract text from element"""
        try:
            if hasattr(element, 'select_one'):
                found = element.select_one(selector)
            else:
                found = element.find_element(By.CSS_SELECTOR, selector)
            return found.get_text(strip=True) if found else ""
        except (NoSuchElementException, AttributeError):
            return ""
    
    def extract_rating(self, element, selector: str) -> float:
        """Extract rating from element"""
        try:
            rating_text = self.extract_text(element, selector)
            # Extract numeric rating from various formats
            import re
            rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
            if rating_match:
                return float(rating_match.group(1))
            return 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def save_data(self, filename: str, format: str = 'csv'):
        """Save scraped data to file"""
        if not self.reviews_data:
            self.logger.warning("No data to save")
            return
        
        df = pd.DataFrame(self.reviews_data)
        
        if format == 'csv':
            df.to_csv(f"{filename}.csv", index=False)
        elif format == 'json':
            df.to_json(f"{filename}.json", orient='records', indent=2)
        elif format == 'excel':
            df.to_excel(f"{filename}.xlsx", index=False)
        
        self.logger.info(f"Data saved to {filename}.{format}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()