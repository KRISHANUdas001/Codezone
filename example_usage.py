"""
Example usage of the review scraper with sample data
"""
import json
import pandas as pd
from datetime import datetime
from sentiment_analyzer import SentimentAnalyzer
from data_processor import DataProcessor

def create_sample_data():
    """Create sample review data for demonstration"""
    sample_reviews = [
        {
            'review_id': 'tp_001',
            'brand': 'Apple',
            'platform': 'trustpilot',
            'country': 'US',
            'rating': 4.5,
            'title': 'Great iPhone experience',
            'review_text': 'I love my new iPhone. The camera quality is amazing and the battery life is excellent. Highly recommended!',
            'reviewer_name': 'John D.',
            'review_date': '2024-01-15',
            'verified_purchase': True,
            'helpful_votes': 12,
            'sentiment_score': 0.0,
            'sentiment_label': '',
            'keywords': [],
            'scraped_at': datetime.now().isoformat()
        },
        {
            'review_id': 'tp_002',
            'brand': 'Apple',
            'platform': 'trustpilot',
            'country': 'UK',
            'rating': 2.0,
            'title': 'Disappointing customer service',
            'review_text': 'The product is okay but the customer service was terrible. Had to wait hours to get help.',
            'reviewer_name': 'Sarah M.',
            'review_date': '2024-01-10',
            'verified_purchase': True,
            'helpful_votes': 8,
            'sentiment_score': 0.0,
            'sentiment_label': '',
            'keywords': [],
            'scraped_at': datetime.now().isoformat()
        },
        {
            'review_id': 'gr_001',
            'brand': 'Samsung',
            'platform': 'google_reviews',
            'country': 'US',
            'rating': 5.0,
            'title': '',
            'review_text': 'Samsung Galaxy is fantastic! Best Android phone I have ever used. Fast, reliable, and great value.',
            'reviewer_name': 'Mike R.',
            'review_date': '2024-01-12',
            'verified_purchase': False,
            'helpful_votes': 5,
            'sentiment_score': 0.0,
            'sentiment_label': '',
            'keywords': [],
            'scraped_at': datetime.now().isoformat()
        },
        {
            'review_id': 'amz_001',
            'brand': 'Samsung',
            'platform': 'amazon',
            'country': 'UK',
            'rating': 3.5,
            'title': 'Good phone but expensive',
            'review_text': 'The Samsung phone works well and has good features, but I think it is overpriced for what you get.',
            'reviewer_name': 'Emma L.',
            'review_date': '2024-01-08',
            'verified_purchase': True,
            'helpful_votes': 3,
            'sentiment_score': 0.0,
            'sentiment_label': '',
            'keywords': [],
            'scraped_at': datetime.now().isoformat()
        },
        {
            'review_id': 'tp_003',
            'brand': 'Microsoft',
            'platform': 'trustpilot',
            'country': 'US',
            'rating': 4.0,
            'title': 'Solid software experience',
            'review_text': 'Microsoft Office suite is reliable and feature-rich. Good for business use.',
            'reviewer_name': 'David K.',
            'review_date': '2024-01-14',
            'verified_purchase': True,
            'helpful_votes': 7,
            'sentiment_score': 0.0,
            'sentiment_label': '',
            'keywords': [],
            'scraped_at': datetime.now().isoformat()
        }
    ]
    
    return sample_reviews

def demonstrate_sentiment_analysis():
    """Demonstrate sentiment analysis functionality"""
    print("🧠 Sentiment Analysis Demo")
    print("=" * 40)
    
    # Create sample data
    reviews = create_sample_data()
    
    # Initialize sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Analyze sentiment for all reviews
    analyzed_reviews = analyzer.analyze_reviews_batch(reviews)
    
    print("📊 Sentiment Analysis Results:")
    print()
    
    for review in analyzed_reviews:
        print(f"Brand: {review['brand']}")
        print(f"Rating: {review['rating']}/5")
        print(f"Review: {review['review_text'][:100]}...")
        print(f"Sentiment Score: {review['sentiment_score']:.3f}")
        print(f"Sentiment Label: {review['sentiment_label']}")
        print(f"Keywords: {', '.join(review['keywords'][:5])}")
        print("-" * 40)
    
    return analyzed_reviews

def demonstrate_data_processing(reviews):
    """Demonstrate data processing functionality"""
    print("\n📈 Data Processing Demo")
    print("=" * 40)
    
    # Initialize data processor
    processor = DataProcessor('demo_output')
    
    # Save data in multiple formats
    saved_files = processor.save_reviews(reviews, 'demo_reviews', ['csv', 'json'])
    
    print("💾 Saved files:")
    for format_type, filepath in saved_files.items():
        print(f"   - {format_type.upper()}: {filepath}")
    
    # Create brand summary
    summary_df = processor.create_brand_summary(reviews)
    print(f"\n📋 Brand Summary:")
    print(summary_df.to_string(index=False))
    
    # Generate dashboard data
    brand_reviews = {}
    for review in reviews:
        brand = review['brand']
        if brand not in brand_reviews:
            brand_reviews[brand] = []
        brand_reviews[brand].append(review)
    
    dashboard_data = processor.create_dashboard_data(brand_reviews)
    
    print(f"\n🎯 Dashboard Summary:")
    print(f"   - Total Reviews: {dashboard_data['summary']['total_reviews']}")
    print(f"   - Total Brands: {dashboard_data['summary']['total_brands']}")
    print(f"   - Average Rating: {dashboard_data['summary']['avg_rating']:.2f}")
    print(f"   - Average Sentiment: {dashboard_data['summary']['avg_sentiment']:.3f}")
    print(f"   - Platforms: {', '.join(dashboard_data['summary']['platforms'])}")
    print(f"   - Countries: {', '.join(dashboard_data['summary']['countries'])}")
    
    return saved_files

def demonstrate_brand_comparison(reviews):
    """Demonstrate brand comparison functionality"""
    print("\n🏆 Brand Comparison Demo")
    print("=" * 40)
    
    # Group reviews by brand
    brand_reviews = {}
    for review in reviews:
        brand = review['brand']
        if brand not in brand_reviews:
            brand_reviews[brand] = []
        brand_reviews[brand].append(review)
    
    # Initialize sentiment analyzer
    analyzer = SentimentAnalyzer()
    
    # Compare brands
    comparison = analyzer.compare_brands(brand_reviews)
    
    print("📊 Brand Comparison Results:")
    print()
    
    for brand, stats in comparison.items():
        print(f"🏢 {brand}:")
        print(f"   - Total Reviews: {stats['total_reviews']}")
        print(f"   - Average Rating: {stats['avg_rating']}/5")
        print(f"   - Average Sentiment: {stats['avg_sentiment']:.3f}")
        print(f"   - Positive Ratio: {stats['positive_ratio']:.1%}")
        print(f"   - Negative Ratio: {stats['negative_ratio']:.1%}")
        print(f"   - Top Keywords: {', '.join([kw[0] for kw in stats['top_5_keywords']])}")
        print()

def main():
    """Run the complete demonstration"""
    print("🎉 Review Scraper Demonstration")
    print("=" * 50)
    print("This demo shows the capabilities of the review scraper")
    print("using sample data (no actual web scraping performed)")
    print()
    
    # Step 1: Sentiment Analysis
    analyzed_reviews = demonstrate_sentiment_analysis()
    
    # Step 2: Data Processing
    saved_files = demonstrate_data_processing(analyzed_reviews)
    
    # Step 3: Brand Comparison
    demonstrate_brand_comparison(analyzed_reviews)
    
    print("\n✅ Demo completed successfully!")
    print("\n📁 To run actual scraping:")
    print("   1. Use: python demo.py")
    print("   2. Or start web dashboard: python web_dashboard.py")
    print("   3. Check README.md for detailed instructions")

if __name__ == "__main__":
    main()