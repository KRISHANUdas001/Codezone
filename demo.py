"""
Demo script to test the review scraper
"""
import os
import sys
from main_scraper import ReviewScraperOrchestrator

def run_demo():
    """Run a simple demo of the scraper"""
    print("🚀 Starting Review Scraper Demo")
    print("=" * 50)
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Initialize scraper
    print("📊 Initializing scraper...")
    scraper = ReviewScraperOrchestrator(headless=True)
    
    # Demo with a small set of brands
    demo_brands = ['Apple', 'Samsung']
    
    print(f"🎯 Target brands: {demo_brands}")
    print("🌍 Countries: US, UK")
    print("🔍 Platforms: Trustpilot")
    print("📝 Max reviews per brand: 10")
    print()
    
    try:
        # Run scraping session
        print("🔄 Starting scraping session...")
        saved_files = scraper.run_full_scraping_session(
            brands=demo_brands,
            countries=['US', 'UK'],
            platforms=['trustpilot'],  # Start with just Trustpilot for demo
            max_reviews_per_brand=10
        )
        
        print("\n✅ Scraping completed successfully!")
        print(f"📁 Generated {len(saved_files)} output files:")
        
        for file_type, file_path in saved_files.items():
            print(f"   - {file_type}: {file_path}")
        
        print("\n📊 Check the 'output' directory for all generated files")
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        print("This might be due to network issues or website changes.")
        print("Check the logs in output/scraper.log for more details.")

if __name__ == "__main__":
    run_demo()