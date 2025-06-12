"""
Main scraper orchestrator
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json
import os

from trustpilot_scraper import TrustpilotScraper
from google_reviews_scraper import GoogleReviewsScraper
from amazon_reviews_scraper import AmazonReviewsScraper
from sentiment_analyzer import SentimentAnalyzer
from data_processor import DataProcessor
from config import BRAND_CATEGORIES, COUNTRIES, SCRAPING_CONFIG, OUTPUT_CONFIG

class ReviewScraperOrchestrator:
    """Main orchestrator for scraping reviews from multiple platforms"""
    
    def __init__(self, output_dir: str = 'output', headless: bool = True):
        self.output_dir = output_dir
        self.headless = headless
        
        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.data_processor = DataProcessor(output_dir)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(output_dir, 'scraper.log')),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def scrape_brand_all_platforms(self, brand_name: str, countries: List[str] = ['US', 'UK'], 
                                 platforms: List[str] = ['trustpilot', 'google_reviews', 'amazon'],
                                 max_reviews_per_platform: int = None) -> Dict[str, List[Dict]]:
        """Scrape reviews for a brand from all specified platforms"""
        
        if max_reviews_per_platform is None:
            max_reviews_per_platform = SCRAPING_CONFIG['max_reviews_per_brand']
        
        self.logger.info(f"Starting scraping for brand: {brand_name}")
        
        all_reviews = []
        platform_results = {}
        
        for country in countries:
            self.logger.info(f"Scraping {brand_name} reviews in {country}")
            
            for platform in platforms:
                try:
                    self.logger.info(f"Scraping from {platform} for {brand_name} in {country}")
                    
                    # Initialize appropriate scraper
                    scraper = self.get_scraper(platform)
                    
                    if scraper:
                        with scraper:
                            reviews = scraper.scrape_brand_reviews(
                                brand_name, country, max_reviews_per_platform
                            )
                            
                            if reviews:
                                # Analyze sentiment and extract keywords
                                reviews = self.sentiment_analyzer.analyze_reviews_batch(reviews)
                                all_reviews.extend(reviews)
                                
                                platform_key = f"{platform}_{country}"
                                platform_results[platform_key] = reviews
                                
                                self.logger.info(f"Successfully scraped {len(reviews)} reviews from {platform} ({country})")
                            else:
                                self.logger.warning(f"No reviews found on {platform} for {brand_name} in {country}")
                    
                except Exception as e:
                    self.logger.error(f"Error scraping {platform} for {brand_name} in {country}: {e}")
                    continue
        
        self.logger.info(f"Completed scraping for {brand_name}. Total reviews: {len(all_reviews)}")
        return {brand_name: all_reviews}
    
    def get_scraper(self, platform: str):
        """Get appropriate scraper instance for platform"""
        scrapers = {
            'trustpilot': TrustpilotScraper,
            'google_reviews': GoogleReviewsScraper,
            'amazon': AmazonReviewsScraper
        }
        
        scraper_class = scrapers.get(platform)
        if scraper_class:
            return scraper_class(headless=self.headless)
        else:
            self.logger.error(f"Unknown platform: {platform}")
            return None
    
    def scrape_multiple_brands(self, brands: List[str], countries: List[str] = ['US', 'UK'],
                             platforms: List[str] = ['trustpilot', 'google_reviews', 'amazon'],
                             max_reviews_per_brand: int = None) -> Dict[str, List[Dict]]:
        """Scrape reviews for multiple brands"""
        
        all_brand_reviews = {}
        
        for brand in brands:
            try:
                brand_reviews = self.scrape_brand_all_platforms(
                    brand, countries, platforms, max_reviews_per_brand
                )
                all_brand_reviews.update(brand_reviews)
                
                # Save individual brand data
                if brand_reviews.get(brand):
                    self.save_brand_data(brand, brand_reviews[brand])
                
            except Exception as e:
                self.logger.error(f"Error scraping brand {brand}: {e}")
                continue
        
        return all_brand_reviews
    
    def scrape_brand_category(self, category: str, countries: List[str] = ['US', 'UK'],
                            platforms: List[str] = ['trustpilot', 'google_reviews', 'amazon'],
                            max_reviews_per_brand: int = None) -> Dict[str, List[Dict]]:
        """Scrape reviews for all brands in a category"""
        
        if category not in BRAND_CATEGORIES:
            self.logger.error(f"Unknown category: {category}")
            return {}
        
        brands = BRAND_CATEGORIES[category]
        self.logger.info(f"Scraping {len(brands)} brands in {category} category")
        
        return self.scrape_multiple_brands(brands, countries, platforms, max_reviews_per_brand)
    
    def save_brand_data(self, brand_name: str, reviews: List[Dict]):
        """Save individual brand data"""
        if not reviews:
            return
        
        # Clean brand name for filename
        safe_brand_name = "".join(c for c in brand_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_brand_name = safe_brand_name.replace(' ', '_')
        
        # Save reviews
        saved_files = self.data_processor.save_reviews(
            reviews, 
            f"brand_{safe_brand_name}",
            OUTPUT_CONFIG['formats']
        )
        
        # Generate visualizations
        plots = self.data_processor.generate_visualizations(reviews, safe_brand_name)
        
        # Create brand summary
        summary = self.sentiment_analyzer.get_brand_sentiment_summary(reviews)
        summary_path = os.path.join(self.output_dir, f"brand_{safe_brand_name}_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"Saved data for {brand_name}: {len(saved_files)} files + visualizations")
    
    def create_complete_dataset(self, brand_reviews: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Create and export complete dataset"""
        self.logger.info("Creating complete dataset...")
        
        # Export complete dataset
        saved_files = self.data_processor.export_complete_dataset(brand_reviews)
        
        # Create brand comparison
        comparison = self.sentiment_analyzer.compare_brands(brand_reviews)
        comparison_path = os.path.join(self.output_dir, "brand_comparison.json")
        with open(comparison_path, 'w') as f:
            json.dump(comparison, f, indent=2, default=str)
        saved_files['comparison'] = comparison_path
        
        self.logger.info(f"Complete dataset created with {len(saved_files)} files")
        return saved_files
    
    def run_full_scraping_session(self, brands: List[str] = None, category: str = None,
                                countries: List[str] = ['US', 'UK'],
                                platforms: List[str] = ['trustpilot', 'google_reviews'],
                                max_reviews_per_brand: int = 50) -> Dict[str, str]:
        """Run a complete scraping session"""
        
        start_time = datetime.now()
        self.logger.info(f"Starting full scraping session at {start_time}")
        
        # Determine brands to scrape
        if brands:
            target_brands = brands
        elif category:
            target_brands = BRAND_CATEGORIES.get(category, [])
        else:
            # Default to technology brands
            target_brands = BRAND_CATEGORIES['technology'][:5]  # Limit for demo
        
        self.logger.info(f"Target brands: {target_brands}")
        self.logger.info(f"Countries: {countries}")
        self.logger.info(f"Platforms: {platforms}")
        
        # Scrape all brands
        all_brand_reviews = self.scrape_multiple_brands(
            target_brands, countries, platforms, max_reviews_per_brand
        )
        
        # Create complete dataset
        saved_files = self.create_complete_dataset(all_brand_reviews)
        
        # Log session summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        total_reviews = sum(len(reviews) for reviews in all_brand_reviews.values())
        
        session_summary = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_minutes': duration.total_seconds() / 60,
            'brands_scraped': len(all_brand_reviews),
            'total_reviews': total_reviews,
            'countries': countries,
            'platforms': platforms,
            'output_files': saved_files
        }
        
        summary_path = os.path.join(self.output_dir, "session_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(session_summary, f, indent=2, default=str)
        
        self.logger.info(f"Scraping session completed in {duration}")
        self.logger.info(f"Total reviews collected: {total_reviews}")
        self.logger.info(f"Output files: {len(saved_files)}")
        
        return saved_files

# Example usage functions
def scrape_technology_brands():
    """Example: Scrape technology brands"""
    scraper = ReviewScraperOrchestrator()
    return scraper.run_full_scraping_session(
        category='technology',
        countries=['US', 'UK'],
        platforms=['trustpilot', 'google_reviews'],
        max_reviews_per_brand=30
    )

def scrape_custom_brands(brand_list: List[str]):
    """Example: Scrape custom list of brands"""
    scraper = ReviewScraperOrchestrator()
    return scraper.run_full_scraping_session(
        brands=brand_list,
        countries=['US', 'UK'],
        platforms=['trustpilot', 'google_reviews', 'amazon'],
        max_reviews_per_brand=50
    )

if __name__ == "__main__":
    # Example usage
    scraper = ReviewScraperOrchestrator()
    
    # Scrape a few technology brands as demo
    demo_brands = ['Apple', 'Samsung', 'Microsoft']
    
    saved_files = scraper.run_full_scraping_session(
        brands=demo_brands,
        countries=['US', 'UK'],
        platforms=['trustpilot'],  # Start with just Trustpilot for demo
        max_reviews_per_brand=20
    )