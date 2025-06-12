"""
Amazon reviews scraper
"""
import re
from datetime import datetime
from urllib.parse import urljoin, quote_plus
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import List, Dict

from scraper_base import BaseScraper
from config import REVIEW_PLATFORMS, SCRAPING_CONFIG

class AmazonReviewsScraper(BaseScraper):
    """Scraper for Amazon product reviews"""
    
    def __init__(self, headless: bool = True):
        super().__init__(headless)
        self.platform_config = REVIEW_PLATFORMS['amazon']
    
    def get_base_url(self, country: str) -> str:
        """Get Amazon base URL for country"""
        if country == 'UK':
            return self.platform_config['uk_url']
        else:
            return self.platform_config['base_url']
    
    def search_products(self, brand_name: str, country: str = 'US') -> List[str]:
        """Search for brand products on Amazon and return product URLs"""
        base_url = self.get_base_url(country)
        tld = 'co.uk' if country == 'UK' else 'com'
        search_url = f"{base_url}/s?k={quote_plus(brand_name)}&ref=nb_sb_noss"
        
        if not self.driver:
            self.setup_driver()
        
        product_urls = []
        
        try:
            self.driver.get(search_url)
            self.wait_for_element('[data-component-type="s-search-result"]', 10)
            
            # Get product links from search results
            product_elements = self.driver.find_elements(
                By.CSS_SELECTOR, 
                '[data-component-type="s-search-result"] h2 a'
            )
            
            for element in product_elements[:10]:  # Take top 10 products
                href = element.get_attribute('href')
                if href:
                    # Convert to full URL if relative
                    if href.startswith('/'):
                        href = urljoin(base_url, href)
                    product_urls.append(href)
            
            return product_urls
            
        except Exception as e:
            self.logger.error(f"Error searching for products: {e}")
            return []
    
    def get_product_reviews_url(self, product_url: str) -> str:
        """Get the reviews URL for a product"""
        try:
            # Extract ASIN from product URL
            asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_url)
            if not asin_match:
                asin_match = re.search(r'/product/([A-Z0-9]{10})', product_url)
            
            if asin_match:
                asin = asin_match.group(1)
                base_url = product_url.split('/dp/')[0] if '/dp/' in product_url else product_url.split('/product/')[0]
                return f"{base_url}/product-reviews/{asin}/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting reviews URL: {e}")
            return None
    
    def scrape_product_reviews(self, product_url: str, brand_name: str, country: str = 'US', max_reviews: int = None) -> List[Dict]:
        """Scrape reviews for a specific product"""
        if max_reviews is None:
            max_reviews = SCRAPING_CONFIG['max_reviews_per_brand'] // 10  # Divide among products
        
        reviews_url = self.get_product_reviews_url(product_url)
        if not reviews_url:
            return []
        
        reviews = []
        page = 1
        
        if not self.driver:
            self.setup_driver()
        
        while len(reviews) < max_reviews:
            page_url = f"{reviews_url}&pageNumber={page}"
            
            try:
                self.driver.get(page_url)
                self.wait_for_element('[data-hook="review"]', 10)
                
                # Get all review elements on the page
                review_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-hook="review"]')
                
                if not review_elements:
                    self.logger.info(f"No more reviews found on page {page}")
                    break
                
                for element in review_elements:
                    if len(reviews) >= max_reviews:
                        break
                    
                    try:
                        review_data = self.extract_review_data(element, brand_name, country, product_url)
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
        
        return reviews
    
    def extract_review_data(self, review_element, brand_name: str, country: str, product_url: str) -> Dict:
        """Extract review data from a review element"""
        try:
            # Rating
            rating = 0.0
            rating_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-hook="review-star-rating"] span')
            if rating_elements:
                rating_text = rating_elements[0].get_attribute('textContent')
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))
            
            # Review title
            title_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-hook="review-title"] span')
            title = ""
            if title_elements:
                title = title_elements[-1].text.strip()  # Last span usually contains the title
            
            # Review text
            text_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-hook="review-body"] span')
            review_text = ""
            if text_elements:
                review_text = text_elements[0].text.strip()
            
            # Reviewer name
            reviewer_elements = review_element.find_elements(By.CSS_SELECTOR, '.a-profile-name')
            reviewer_name = ""
            if reviewer_elements:
                reviewer_name = reviewer_elements[0].text.strip()
            
            # Review date
            date_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-hook="review-date"]')
            review_date = ""
            if date_elements:
                date_text = date_elements[0].text.strip()
                # Extract date from "Reviewed in [Country] on [Date]" format
                date_match = re.search(r'on (.+)$', date_text)
                if date_match:
                    review_date = date_match.group(1)
            
            # Verified purchase
            verified_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-hook="avp-badge"]')
            verified_purchase = len(verified_elements) > 0
            
            # Helpful votes
            helpful_votes = 0
            helpful_elements = review_element.find_elements(By.CSS_SELECTOR, '[data-hook="helpful-vote-statement"]')
            if helpful_elements:
                helpful_text = helpful_elements[0].text
                helpful_match = re.search(r'(\d+)', helpful_text)
                if helpful_match:
                    helpful_votes = int(helpful_match.group(1))
            
            # Product info
            product_name = self.get_product_name(product_url)
            
            return {
                'review_id': f"amz_{hash(review_text + reviewer_name + str(rating))}",
                'brand': brand_name,
                'platform': 'amazon',
                'country': country,
                'rating': rating,
                'title': title,
                'review_text': review_text,
                'reviewer_name': reviewer_name,
                'review_date': review_date,
                'verified_purchase': verified_purchase,
                'helpful_votes': helpful_votes,
                'product_name': product_name,
                'product_url': product_url,
                'sentiment_score': 0.0,
                'sentiment_label': '',
                'keywords': [],
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting Amazon review data: {e}")
            return None
    
    def get_product_name(self, product_url: str) -> str:
        """Get product name from URL or page"""
        try:
            if not self.driver.current_url == product_url:
                self.driver.get(product_url)
                self.wait_for_element('#productTitle', 5)
            
            title_element = self.driver.find_element(By.CSS_SELECTOR, '#productTitle')
            return title_element.text.strip()
            
        except Exception:
            return ""
    
    def scrape_brand_reviews(self, brand_name: str, country: str = 'US', max_reviews: int = None) -> List[Dict]:
        """Main method to scrape all reviews for a brand"""
        self.logger.info(f"Starting Amazon scraping for {brand_name} in {country}")
        
        # Search for products
        product_urls = self.search_products(brand_name, country)
        
        if not product_urls:
            self.logger.warning(f"No Amazon products found for {brand_name}")
            return []
        
        all_reviews = []
        reviews_per_product = max_reviews // len(product_urls) if max_reviews else 10
        
        # Scrape reviews from each product
        for product_url in product_urls:
            try:
                reviews = self.scrape_product_reviews(
                    product_url, brand_name, country, reviews_per_product
                )
                all_reviews.extend(reviews)
                
                if max_reviews and len(all_reviews) >= max_reviews:
                    all_reviews = all_reviews[:max_reviews]
                    break
                    
            except Exception as e:
                self.logger.error(f"Error scraping product {product_url}: {e}")
                continue
        
        self.reviews_data.extend(all_reviews)
        return all_reviews