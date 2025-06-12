"""
Google Reviews scraper
"""
import re
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict

from scraper_base import BaseScraper
from config import REVIEW_PLATFORMS, SCRAPING_CONFIG

class GoogleReviewsScraper(BaseScraper):
    """Scraper for Google Reviews"""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_config = REVIEW_PLATFORMS['google_reviews']
        self.base_url = self.platform_config['base_url']
    
    def search_business(self, brand_name: str, country: str = 'US') -> str:
        """Search for business on Google Maps and return the reviews URL"""
        if country == 'UK':
            search_query = f"{brand_name} UK reviews site:google.com"
        else:
            search_query = f"{brand_name} reviews site:google.com"
        
        search_url = f"https://www.google.com/search?q={search_query.replace(' ', '+')}"
        
        if not self.driver:
            self.setup_driver()
        
        try:
            self.driver.get(search_url)
            self.wait_for_element('a[href*="maps.google.com"]', 10)
            
            # Look for Google Maps links
            maps_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="maps.google.com"]')
            
            for link in maps_links:
                href = link.get_attribute('href')
                if 'place' in href or 'search' in href:
                    return href
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching for business {brand_name}: {e}")
            return None
    
    def scrape_reviews(self, maps_url: str, brand_name: str, country: str = 'US', max_reviews: int = None) -> List[Dict]:
        """Scrape reviews from Google Maps business page"""
        if max_reviews is None:
            max_reviews = SCRAPING_CONFIG['max_reviews_per_brand']
        
        reviews = []
        
        if not self.driver:
            self.setup_driver()
        
        try:
            self.driver.get(maps_url)
            
            # Wait for the page to load and look for reviews section
            self.wait_for_element('[data-review-id]', 15)
            
            # Click on reviews tab if it exists
            try:
                reviews_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab-index="1"]')
                reviews_tab.click()
                self.random_delay(2, 3)
            except NoSuchElementException:
                pass
            
            # Scroll to load more reviews
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while len(reviews) < max_reviews and scroll_attempts < max_scroll_attempts:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.random_delay(2, 3)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = new_height
                
                # Extract reviews from current page
                review_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-review-id]')
                
                for element in review_elements[len(reviews):]:
                    if len(reviews) >= max_reviews:
                        break
                    
                    try:
                        review_data = self.extract_review_data(element, brand_name, country)
                        if review_data and review_data not in reviews:
                            reviews.append(review_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting review: {e}")
                        continue
            
        except Exception as e:
            self.logger.error(f"Error scraping Google reviews: {e}")
        
        self.logger.info(f"Scraped {len(reviews)} reviews for {brand_name} from Google")
        return reviews
    
    def extract_review_data(self, review_element, brand_name: str, country: str) -> Dict:
        """Extract review data from a review element"""
        try:
            # Rating
            rating = 0.0
            rating_elements = review_element.find_elements(By.CSS_SELECTOR, '[role="img"][aria-label*="star"]')
            if rating_elements:
                aria_label = rating_elements[0].get_attribute('aria-label')
                rating_match = re.search(r'(\d+)', aria_label)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Review text
            text_elements = review_element.find_elements(By.CSS_SELECTOR, '[jsname="bN97Pc"]')
            review_text = ""
            if text_elements:
                review_text = text_elements[0].text.strip()
            
            # Reviewer name
            reviewer_elements = review_element.find_elements(By.CSS_SELECTOR, '.X43Kjb')
            reviewer_name = ""
            if reviewer_elements:
                reviewer_name = reviewer_elements[0].text.strip()
            
            # Review date
            date_elements = review_element.find_elements(By.CSS_SELECTOR, '.rsqaWe')
            review_date = ""
            if date_elements:
                review_date = date_elements[0].text.strip()
            
            # Convert relative date to approximate date
            review_date = self.parse_relative_date(review_date)
            
            # Review ID
            review_id = review_element.get_attribute('data-review-id')
            if not review_id:
                review_id = f"gr_{hash(review_text + reviewer_name + str(rating))}"
            
            return {
                'review_id': review_id,
                'brand': brand_name,
                'platform': 'google_reviews',
                'country': country,
                'rating': rating,
                'title': '',  # Google reviews don't typically have titles
                'review_text': review_text,
                'reviewer_name': reviewer_name,
                'review_date': review_date,
                'verified_purchase': False,  # Google doesn't show purchase verification
                'helpful_votes': 0,  # Not easily accessible
                'sentiment_score': 0.0,
                'sentiment_label': '',
                'keywords': [],
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting Google review data: {e}")
            return None
    
    def parse_relative_date(self, date_str: str) -> str:
        """Convert relative date strings to approximate dates"""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        date_str = date_str.lower()
        
        if 'day' in date_str:
            days_match = re.search(r'(\d+)', date_str)
            if days_match:
                days = int(days_match.group(1))
                return (now - timedelta(days=days)).strftime('%Y-%m-%d')
        elif 'week' in date_str:
            weeks_match = re.search(r'(\d+)', date_str)
            if weeks_match:
                weeks = int(weeks_match.group(1))
                return (now - timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        elif 'month' in date_str:
            months_match = re.search(r'(\d+)', date_str)
            if months_match:
                months = int(months_match.group(1))
                return (now - timedelta(days=months*30)).strftime('%Y-%m-%d')
        elif 'year' in date_str:
            years_match = re.search(r'(\d+)', date_str)
            if years_match:
                years = int(years_match.group(1))
                return (now - timedelta(days=years*365)).strftime('%Y-%m-%d')
        
        return now.strftime('%Y-%m-%d')
    
    def scrape_brand_reviews(self, brand_name: str, country: str = 'US', max_reviews: int = None) -> List[Dict]:
        """Main method to scrape all reviews for a brand"""
        self.logger.info(f"Starting Google Reviews scraping for {brand_name} in {country}")
        
        # Search for the business
        maps_url = self.search_business(brand_name, country)
        
        if not maps_url:
            self.logger.warning(f"No Google Maps page found for {brand_name}")
            return []
        
        # Scrape reviews
        reviews = self.scrape_reviews(maps_url, brand_name, country, max_reviews)
        
        self.reviews_data.extend(reviews)
        return reviews