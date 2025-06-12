"""
Trustpilot review scraper
"""
import re
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Dict

from scraper_base import BaseScraper
from config import REVIEW_PLATFORMS, SCRAPING_CONFIG

class TrustpilotScraper(BaseScraper):
    """Scraper for Trustpilot reviews"""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_config = REVIEW_PLATFORMS['trustpilot']
        self.base_url = self.platform_config['base_url']
    
    def search_brand(self, brand_name: str, country: str = 'US') -> List[str]:
        """Search for brand on Trustpilot and return company URLs"""
        search_url = f"{self.base_url}/search?query={brand_name.replace(' ', '+')}"
        
        if not self.driver:
            self.setup_driver()
        
        try:
            self.driver.get(search_url)
            self.wait_for_element('[data-business-unit-reviews-count-link]', 10)
            
            # Find company links
            company_links = []
            elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-business-unit-reviews-count-link]')
            
            for element in elements[:3]:  # Take top 3 results
                href = element.get_attribute('href')
                if href:
                    company_links.append(href)
            
            return company_links
            
        except Exception as e:
            self.logger.error(f"Error searching for brand {brand_name}: {e}")
            return []
    
    def scrape_reviews(self, company_url: str, brand_name: str, country: str = 'US', max_reviews: int = None) -> List[Dict]:
        """Scrape reviews from a Trustpilot company page"""
        if max_reviews is None:
            max_reviews = SCRAPING_CONFIG['max_reviews_per_brand']
        
        reviews = []
        page = 1
        
        if not self.driver:
            self.setup_driver()
        
        while len(reviews) < max_reviews:
            page_url = f"{company_url}?page={page}"
            
            try:
                self.driver.get(page_url)
                self.wait_for_element('[data-service-review-card-paper]', 10)
                
                # Get all review cards on the page
                review_cards = self.driver.find_elements(By.CSS_SELECTOR, '[data-service-review-card-paper]')
                
                if not review_cards:
                    self.logger.info(f"No more reviews found on page {page}")
                    break
                
                for card in review_cards:
                    if len(reviews) >= max_reviews:
                        break
                    
                    try:
                        review_data = self.extract_review_data(card, brand_name, country)
                        if review_data:
                            reviews.append(review_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting review: {e}")
                        continue
                
                page += 1
                self.random_delay(2, 4)
                
            except Exception as e:
                self.logger.error(f"Error scraping page {page}: {e}")
                break
        
        self.logger.info(f"Scraped {len(reviews)} reviews for {brand_name} from Trustpilot")
        return reviews
    
    def extract_review_data(self, review_element, brand_name: str, country: str) -> Dict:
        """Extract review data from a review element"""
        try:
            # Rating
            rating_element = review_element.find_element(By.CSS_SELECTOR, '[data-service-review-rating]')
            rating = float(rating_element.get_attribute('data-service-review-rating'))
            
            # Review title
            title_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-service-review-title-typography="true"]')
            title = title_elements[0].text.strip() if title_elements else ""
            
            # Review text
            text_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-service-review-text-typography="true"]')
            review_text = text_elements[0].text.strip() if text_elements else ""
            
            # Reviewer name
            reviewer_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-consumer-name-typography="true"]')
            reviewer_name = reviewer_elements[0].text.strip() if reviewer_elements else ""
            
            # Review date
            date_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-service-review-date-time-ago]')
            review_date = date_elements[0].get_attribute('datetime') if date_elements else ""
            
            # Verified purchase (Trustpilot shows verified reviews)
            verified_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-service-review-source]')
            verified_purchase = len(verified_elements) > 0
            
            # Helpful votes
            helpful_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-service-review-helpful-count]')
            helpful_votes = 0
            if helpful_elements:
                helpful_text = helpful_elements[0].text
                helpful_match = re.search(r'(\d+)', helpful_text)
                if helpful_match:
                    helpful_votes = int(helpful_match.group(1))
            
            return {
                'review_id': f"tp_{hash(review_text + reviewer_name + str(rating))}",
                'brand': brand_name,
                'platform': 'trustpilot',
                'country': country,
                'rating': rating,
                'title': title,
                'review_text': review_text,
                'reviewer_name': reviewer_name,
                'review_date': review_date,
                'verified_purchase': verified_purchase,
                'helpful_votes': helpful_votes,
                'sentiment_score': 0.0,  # To be calculated later
                'sentiment_label': '',   # To be calculated later
                'keywords': [],          # To be extracted later
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting review data: {e}")
            return None
    
    def scrape_brand_reviews(self, brand_name: str, country: str = 'US', max_reviews: int = None) -> List[Dict]:
        """Main method to scrape all reviews for a brand"""
        self.logger.info(f"Starting Trustpilot scraping for {brand_name} in {country}")
        
        # Search for the brand
        company_urls = self.search_brand(brand_name, country)
        
        if not company_urls:
            self.logger.warning(f"No Trustpilot pages found for {brand_name}")
            return []
        
        all_reviews = []
        
        # Scrape reviews from each company page found
        for url in company_urls:
            reviews = self.scrape_reviews(url, brand_name, country, max_reviews)
            all_reviews.extend(reviews)
            
            if max_reviews and len(all_reviews) >= max_reviews:
                all_reviews = all_reviews[:max_reviews]
                break
        
        self.reviews_data.extend(all_reviews)
        return all_reviews