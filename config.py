"""
Configuration file for the review scraper
"""
import os
from typing import Dict, List

# Supported review platforms
REVIEW_PLATFORMS = {
    'trustpilot': {
        'base_url': 'https://www.trustpilot.com',
        'search_url': 'https://www.trustpilot.com/review/{domain}',
        'rating_selector': '.star-rating_starRating__4rrcf',
        'review_selector': '.typography_body-l__KUYFJ',
        'title_selector': '.typography_heading-s__f7029',
        'date_selector': '.typography_body-m__xgxZ_',
        'reviewer_selector': '.typography_heading-xxs__QKBS8'
    },
    'google_reviews': {
        'base_url': 'https://www.google.com',
        'search_url': 'https://www.google.com/search?q={brand}+reviews',
        'rating_selector': '[data-value]',
        'review_selector': '[data-review-id] span[jsname="bN97Pc"]',
        'title_selector': '[data-review-id] .TSUbDb',
        'date_selector': '[data-review-id] .rsqaWe',
        'reviewer_selector': '[data-review-id] .X43Kjb'
    },
    'amazon': {
        'base_url': 'https://www.amazon.com',
        'uk_url': 'https://www.amazon.co.uk',
        'search_url': 'https://www.amazon.{tld}/s?k={brand}',
        'rating_selector': '[data-hook="review-star-rating"] span',
        'review_selector': '[data-hook="review-body"] span',
        'title_selector': '[data-hook="review-title"] span',
        'date_selector': '[data-hook="review-date"]',
        'reviewer_selector': '.a-profile-name'
    },
    'yelp': {
        'base_url': 'https://www.yelp.com',
        'uk_url': 'https://www.yelp.co.uk',
        'search_url': 'https://www.yelp.{tld}/biz/{business_name}',
        'rating_selector': '.i-stars',
        'review_selector': '.raw__09f24__T4Ezm',
        'title_selector': '.css-1m051bw',
        'date_selector': '.css-chan6m',
        'reviewer_selector': '.css-1m051bw'
    }
}

# Target countries and their configurations
COUNTRIES = {
    'UK': {
        'domains': ['co.uk', 'uk'],
        'currency': 'GBP',
        'language': 'en-GB'
    },
    'US': {
        'domains': ['com'],
        'currency': 'USD',
        'language': 'en-US'
    }
}

# Common brand categories to scrape
BRAND_CATEGORIES = {
    'technology': [
        'Apple', 'Samsung', 'Microsoft', 'Google', 'Amazon', 'Sony', 'Dell', 'HP', 'Lenovo', 'ASUS'
    ],
    'fashion': [
        'Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo', 'ASOS', 'Next', 'Marks & Spencer', 'Primark', 'Burberry'
    ],
    'automotive': [
        'BMW', 'Mercedes-Benz', 'Audi', 'Toyota', 'Honda', 'Ford', 'Volkswagen', 'Tesla', 'Jaguar', 'Land Rover'
    ],
    'food_beverage': [
        'McDonald\'s', 'KFC', 'Starbucks', 'Subway', 'Pizza Hut', 'Domino\'s', 'Coca-Cola', 'Pepsi', 'Nestle', 'Tesco'
    ],
    'retail': [
        'Walmart', 'Target', 'Best Buy', 'John Lewis', 'Argos', 'Currys', 'B&Q', 'IKEA', 'Sainsbury\'s', 'ASDA'
    ]
}

# Scraping settings
SCRAPING_CONFIG = {
    'delay_between_requests': 2,  # seconds
    'max_retries': 3,
    'timeout': 30,
    'max_reviews_per_brand': 100,
    'user_agents': [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
}

# Output settings
OUTPUT_CONFIG = {
    'formats': ['csv', 'json', 'excel'],
    'include_sentiment': True,
    'include_keywords': True,
    'generate_summary': True
}

# Database schema for reviews
REVIEW_SCHEMA = {
    'review_id': str,
    'brand': str,
    'platform': str,
    'country': str,
    'rating': float,
    'title': str,
    'review_text': str,
    'reviewer_name': str,
    'review_date': str,
    'verified_purchase': bool,
    'helpful_votes': int,
    'sentiment_score': float,
    'sentiment_label': str,
    'keywords': list,
    'scraped_at': str
}