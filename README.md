# Brand Review Scraper

A comprehensive web scraper for collecting customer review data from multiple platforms (Trustpilot, Google Reviews, Amazon) for brands in the UK and US markets. The scraper includes sentiment analysis, keyword extraction, and data visualization capabilities.

## Features

- **Multi-Platform Scraping**: Supports Trustpilot, Google Reviews, and Amazon
- **Multi-Country Support**: UK and US markets
- **Sentiment Analysis**: Automatic sentiment scoring and classification
- **Keyword Extraction**: Identifies key themes in reviews
- **Data Export**: CSV, JSON, and Excel formats
- **Visualizations**: Charts and word clouds
- **Web Dashboard**: Interactive interface for managing scraping and viewing results
- **Brand Categories**: Pre-defined categories (Technology, Fashion, Automotive, etc.)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Install Chrome WebDriver** (automatically handled by webdriver-manager)

## Quick Start

### Option 1: Web Dashboard (Recommended)

1. **Start the web dashboard**:
```bash
python web_dashboard.py
```

2. **Open your browser** and go to `http://localhost:12000`

3. **Use the interface** to:
   - Enter brand names (comma-separated)
   - Select countries (US, UK)
   - Choose platforms (Trustpilot, Google Reviews, Amazon)
   - Set maximum reviews per brand
   - Start scraping and view results

### Option 2: Command Line

```python
from main_scraper import ReviewScraperOrchestrator

# Initialize scraper
scraper = ReviewScraperOrchestrator()

# Scrape specific brands
brands = ['Apple', 'Samsung', 'Microsoft']
saved_files = scraper.run_full_scraping_session(
    brands=brands,
    countries=['US', 'UK'],
    platforms=['trustpilot', 'google_reviews'],
    max_reviews_per_brand=50
)

print(f"Data saved to: {saved_files}")
```

### Option 3: Category-Based Scraping

```python
from main_scraper import scrape_technology_brands

# Scrape all technology brands
saved_files = scrape_technology_brands()
```

## Configuration

### Brand Categories

The scraper includes pre-defined brand categories in `config.py`:

- **Technology**: Apple, Samsung, Microsoft, Google, Amazon, etc.
- **Fashion**: Nike, Adidas, Zara, H&M, Uniqlo, etc.
- **Automotive**: BMW, Mercedes-Benz, Audi, Toyota, Honda, etc.
- **Food & Beverage**: McDonald's, KFC, Starbucks, Subway, etc.
- **Retail**: Walmart, Target, Best Buy, John Lewis, etc.

### Scraping Settings

Modify `config.py` to adjust:

- `max_reviews_per_brand`: Maximum reviews to collect per brand
- `delay_between_requests`: Delay between HTTP requests
- `timeout`: Request timeout duration
- `user_agents`: List of user agents for rotation

## Output Files

The scraper generates several types of output files:

### Data Files
- `brand_reviews_dataset_[timestamp].csv` - Complete dataset
- `brand_reviews_dataset_[timestamp].json` - JSON format
- `brand_reviews_dataset_[timestamp].xlsx` - Excel format
- `brand_[name]_summary.json` - Individual brand summaries

### Visualizations
- `rating_distribution_[brand].png` - Rating distribution charts
- `sentiment_distribution_[brand].png` - Sentiment analysis charts
- `platform_comparison_[brand].png` - Platform comparison
- `keywords_wordcloud_[brand].png` - Word clouds

### Analysis Files
- `brand_comparison.json` - Cross-brand comparison
- `session_summary.json` - Scraping session details
- `scraper.log` - Detailed logs

## Data Schema

Each review record contains:

```json
{
    "review_id": "unique_identifier",
    "brand": "Brand Name",
    "platform": "trustpilot|google_reviews|amazon",
    "country": "US|UK",
    "rating": 4.5,
    "title": "Review Title",
    "review_text": "Review content...",
    "reviewer_name": "Reviewer Name",
    "review_date": "2024-01-15",
    "verified_purchase": true,
    "helpful_votes": 5,
    "sentiment_score": 0.75,
    "sentiment_label": "positive|negative|neutral",
    "keywords": ["quality", "service", "price"],
    "scraped_at": "2024-01-15T10:30:00"
}
```

## Platform-Specific Features

### Trustpilot
- Company search and review extraction
- Verified review detection
- Helpful vote counts
- Multi-page scraping

### Google Reviews
- Business search via Google Maps
- Relative date parsing
- Infinite scroll handling
- Rating extraction from aria-labels

### Amazon
- Product search and review extraction
- Verified purchase detection
- Product-specific reviews
- Multi-product aggregation

## Advanced Usage

### Custom Scraper Configuration

```python
from main_scraper import ReviewScraperOrchestrator

# Custom configuration
scraper = ReviewScraperOrchestrator(
    output_dir='custom_output',
    headless=False  # Show browser for debugging
)

# Scrape with custom parameters
brand_reviews = scraper.scrape_multiple_brands(
    brands=['Custom Brand 1', 'Custom Brand 2'],
    countries=['US'],
    platforms=['trustpilot'],
    max_reviews_per_brand=100
)
```

### Sentiment Analysis Only

```python
from sentiment_analyzer import SentimentAnalyzer

analyzer = SentimentAnalyzer()

# Analyze existing reviews
reviews = [...]  # Your review data
analyzed_reviews = analyzer.analyze_reviews_batch(reviews)

# Get brand summary
summary = analyzer.get_brand_sentiment_summary(analyzed_reviews)
```

### Data Processing Only

```python
from data_processor import DataProcessor

processor = DataProcessor()

# Load and process existing data
reviews = [...]  # Your review data
saved_files = processor.save_reviews(reviews, 'processed_data')

# Generate visualizations
plots = processor.generate_visualizations(reviews, 'Brand Name')
```

## Troubleshooting

### Common Issues

1. **Chrome Driver Issues**:
   - The scraper automatically downloads ChromeDriver
   - Ensure Chrome browser is installed
   - For headless issues, set `headless=False` for debugging

2. **Rate Limiting**:
   - Increase delays in `config.py`
   - Use fewer concurrent requests
   - Consider using proxies for large-scale scraping

3. **Element Not Found**:
   - Websites may change their structure
   - Update selectors in platform-specific scrapers
   - Check browser console for errors

4. **Memory Issues**:
   - Reduce `max_reviews_per_brand`
   - Process brands individually
   - Clear browser cache between sessions

### Debugging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Run with visible browser:

```python
scraper = ReviewScraperOrchestrator(headless=False)
```

## Legal and Ethical Considerations

- **Respect robots.txt**: Check website policies before scraping
- **Rate Limiting**: Use appropriate delays between requests
- **Terms of Service**: Ensure compliance with platform terms
- **Data Privacy**: Handle personal data responsibly
- **Commercial Use**: Check licensing requirements for commercial applications

## Performance Tips

1. **Optimize for Speed**:
   - Use headless mode for production
   - Implement parallel processing for multiple brands
   - Cache frequently accessed data

2. **Resource Management**:
   - Close browser sessions properly
   - Monitor memory usage
   - Use database storage for large datasets

3. **Reliability**:
   - Implement retry logic
   - Handle network timeouts gracefully
   - Save progress incrementally

## Contributing

To extend the scraper:

1. **Add New Platforms**: Create new scraper classes inheriting from `BaseScraper`
2. **Improve Selectors**: Update CSS selectors for better reliability
3. **Add Features**: Implement additional analysis or export options
4. **Optimize Performance**: Improve speed and resource usage

## License

This project is for educational and research purposes. Ensure compliance with website terms of service and applicable laws when using for commercial purposes.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `output/scraper.log`
3. Test with a small dataset first
4. Ensure all dependencies are properly installed