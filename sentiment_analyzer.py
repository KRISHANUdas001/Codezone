"""
Sentiment analysis and text processing utilities
"""
import re
import nltk
from textblob import TextBlob
from collections import Counter
from typing import List, Dict, Tuple
import pandas as pd
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

class SentimentAnalyzer:
    """Sentiment analysis and keyword extraction for reviews"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.logger = logging.getLogger(__name__)
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """
        Analyze sentiment of text using TextBlob
        Returns: (sentiment_score, sentiment_label)
        """
        if not text or not text.strip():
            return 0.0, 'neutral'
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Convert polarity to label
            if polarity > 0.1:
                label = 'positive'
            elif polarity < -0.1:
                label = 'negative'
            else:
                label = 'neutral'
            
            return polarity, label
            
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return 0.0, 'neutral'
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text using POS tagging and frequency analysis"""
        if not text or not text.strip():
            return []
        
        try:
            # Clean and tokenize text
            cleaned_text = self.clean_text(text)
            tokens = word_tokenize(cleaned_text.lower())
            
            # Remove stopwords and short words
            filtered_tokens = [
                word for word in tokens 
                if word not in self.stop_words 
                and len(word) > 2 
                and word.isalpha()
            ]
            
            # POS tagging to get nouns and adjectives
            pos_tags = pos_tag(filtered_tokens)
            keywords = [
                word for word, pos in pos_tags 
                if pos.startswith('NN') or pos.startswith('JJ')  # Nouns and adjectives
            ]
            
            # Get most frequent keywords
            keyword_freq = Counter(keywords)
            top_keywords = [word for word, freq in keyword_freq.most_common(max_keywords)]
            
            return top_keywords
            
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean text for processing"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep spaces and basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\-]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def analyze_reviews_batch(self, reviews: List[Dict]) -> List[Dict]:
        """Analyze sentiment and extract keywords for a batch of reviews"""
        self.logger.info(f"Analyzing sentiment for {len(reviews)} reviews")
        
        for review in reviews:
            # Combine title and review text for analysis
            full_text = f"{review.get('title', '')} {review.get('review_text', '')}"
            
            # Analyze sentiment
            sentiment_score, sentiment_label = self.analyze_sentiment(full_text)
            review['sentiment_score'] = sentiment_score
            review['sentiment_label'] = sentiment_label
            
            # Extract keywords
            keywords = self.extract_keywords(full_text)
            review['keywords'] = keywords
        
        return reviews
    
    def get_brand_sentiment_summary(self, reviews: List[Dict]) -> Dict:
        """Generate sentiment summary for a brand"""
        if not reviews:
            return {}
        
        df = pd.DataFrame(reviews)
        
        summary = {
            'total_reviews': len(reviews),
            'average_rating': df['rating'].mean(),
            'average_sentiment': df['sentiment_score'].mean(),
            'sentiment_distribution': df['sentiment_label'].value_counts().to_dict(),
            'rating_distribution': df['rating'].value_counts().sort_index().to_dict(),
            'top_keywords': self.get_top_keywords_from_reviews(reviews),
            'platform_breakdown': df['platform'].value_counts().to_dict(),
            'country_breakdown': df['country'].value_counts().to_dict()
        }
        
        return summary
    
    def get_top_keywords_from_reviews(self, reviews: List[Dict], top_n: int = 20) -> List[Tuple[str, int]]:
        """Get top keywords across all reviews"""
        all_keywords = []
        
        for review in reviews:
            keywords = review.get('keywords', [])
            all_keywords.extend(keywords)
        
        keyword_freq = Counter(all_keywords)
        return keyword_freq.most_common(top_n)
    
    def compare_brands(self, brand_reviews: Dict[str, List[Dict]]) -> Dict:
        """Compare sentiment and ratings across multiple brands"""
        comparison = {}
        
        for brand, reviews in brand_reviews.items():
            if reviews:
                summary = self.get_brand_sentiment_summary(reviews)
                comparison[brand] = {
                    'total_reviews': summary['total_reviews'],
                    'avg_rating': round(summary['average_rating'], 2),
                    'avg_sentiment': round(summary['average_sentiment'], 3),
                    'positive_ratio': summary['sentiment_distribution'].get('positive', 0) / summary['total_reviews'],
                    'negative_ratio': summary['sentiment_distribution'].get('negative', 0) / summary['total_reviews'],
                    'top_5_keywords': summary['top_keywords'][:5]
                }
        
        return comparison