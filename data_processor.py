"""
Data processing and export utilities
"""
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import logging

class DataProcessor:
    """Process and export scraped review data"""
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def save_reviews(self, reviews: List[Dict], filename: str, formats: List[str] = ['csv', 'json', 'excel']) -> Dict[str, str]:
        """Save reviews in multiple formats"""
        saved_files = {}
        
        if not reviews:
            self.logger.warning("No reviews to save")
            return saved_files
        
        df = pd.DataFrame(reviews)
        
        # Clean the data
        df = self.clean_dataframe(df)
        
        # Save in requested formats
        for format_type in formats:
            try:
                if format_type == 'csv':
                    filepath = os.path.join(self.output_dir, f"{filename}.csv")
                    df.to_csv(filepath, index=False, encoding='utf-8')
                    saved_files['csv'] = filepath
                
                elif format_type == 'json':
                    filepath = os.path.join(self.output_dir, f"{filename}.json")
                    df.to_json(filepath, orient='records', indent=2)
                    saved_files['json'] = filepath
                
                elif format_type == 'excel':
                    filepath = os.path.join(self.output_dir, f"{filename}.xlsx")
                    df.to_excel(filepath, index=False, engine='openpyxl')
                    saved_files['excel'] = filepath
                
                self.logger.info(f"Saved {len(reviews)} reviews to {filepath}")
                
            except Exception as e:
                self.logger.error(f"Error saving {format_type} file: {e}")
        
        return saved_files
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the dataframe"""
        # Convert rating to numeric
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Convert sentiment_score to numeric
        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
        
        # Convert helpful_votes to numeric
        df['helpful_votes'] = pd.to_numeric(df['helpful_votes'], errors='coerce').fillna(0)
        
        # Clean text fields
        text_columns = ['title', 'review_text', 'reviewer_name']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Convert keywords list to string for CSV compatibility
        if 'keywords' in df.columns:
            df['keywords_str'] = df['keywords'].apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x))
        
        # Sort by brand and rating
        df = df.sort_values(['brand', 'rating'], ascending=[True, False])
        
        return df
    
    def create_brand_summary(self, reviews: List[Dict]) -> pd.DataFrame:
        """Create a summary dataframe by brand"""
        if not reviews:
            return pd.DataFrame()
        
        df = pd.DataFrame(reviews)
        
        summary = df.groupby('brand').agg({
            'rating': ['count', 'mean', 'std'],
            'sentiment_score': ['mean', 'std'],
            'helpful_votes': 'sum',
            'platform': lambda x: ', '.join(x.unique()),
            'country': lambda x: ', '.join(x.unique())
        }).round(2)
        
        # Flatten column names
        summary.columns = ['_'.join(col).strip() for col in summary.columns]
        summary = summary.reset_index()
        
        # Rename columns for clarity
        column_mapping = {
            'rating_count': 'total_reviews',
            'rating_mean': 'avg_rating',
            'rating_std': 'rating_std',
            'sentiment_score_mean': 'avg_sentiment',
            'sentiment_score_std': 'sentiment_std',
            'helpful_votes_sum': 'total_helpful_votes',
            'platform_<lambda>': 'platforms',
            'country_<lambda>': 'countries'
        }
        
        summary = summary.rename(columns=column_mapping)
        
        return summary
    
    def generate_visualizations(self, reviews: List[Dict], brand_name: str = None) -> Dict[str, str]:
        """Generate visualization charts for the data"""
        if not reviews:
            return {}
        
        df = pd.DataFrame(reviews)
        saved_plots = {}
        
        # Set style
        plt.style.use('seaborn-v0_8')
        
        try:
            # 1. Rating distribution
            plt.figure(figsize=(10, 6))
            df['rating'].hist(bins=5, edgecolor='black', alpha=0.7)
            plt.title(f'Rating Distribution{" - " + brand_name if brand_name else ""}')
            plt.xlabel('Rating')
            plt.ylabel('Number of Reviews')
            plt.grid(True, alpha=0.3)
            
            plot_path = os.path.join(self.output_dir, f'rating_distribution_{brand_name or "all"}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            saved_plots['rating_distribution'] = plot_path
            
            # 2. Sentiment distribution
            plt.figure(figsize=(8, 6))
            sentiment_counts = df['sentiment_label'].value_counts()
            colors = ['green', 'red', 'gray']
            sentiment_counts.plot(kind='bar', color=colors[:len(sentiment_counts)])
            plt.title(f'Sentiment Distribution{" - " + brand_name if brand_name else ""}')
            plt.xlabel('Sentiment')
            plt.ylabel('Number of Reviews')
            plt.xticks(rotation=0)
            plt.grid(True, alpha=0.3)
            
            plot_path = os.path.join(self.output_dir, f'sentiment_distribution_{brand_name or "all"}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            saved_plots['sentiment_distribution'] = plot_path
            
            # 3. Platform comparison
            if len(df['platform'].unique()) > 1:
                plt.figure(figsize=(10, 6))
                platform_ratings = df.groupby('platform')['rating'].mean()
                platform_ratings.plot(kind='bar', color='skyblue')
                plt.title(f'Average Rating by Platform{" - " + brand_name if brand_name else ""}')
                plt.xlabel('Platform')
                plt.ylabel('Average Rating')
                plt.xticks(rotation=45)
                plt.grid(True, alpha=0.3)
                
                plot_path = os.path.join(self.output_dir, f'platform_comparison_{brand_name or "all"}.png')
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                saved_plots['platform_comparison'] = plot_path
            
            # 4. Word cloud from keywords
            all_keywords = []
            for review in reviews:
                keywords = review.get('keywords', [])
                all_keywords.extend(keywords)
            
            if all_keywords:
                keyword_text = ' '.join(all_keywords)
                wordcloud = WordCloud(
                    width=800, height=400, 
                    background_color='white',
                    max_words=100
                ).generate(keyword_text)
                
                plt.figure(figsize=(12, 6))
                plt.imshow(wordcloud, interpolation='bilinear')
                plt.axis('off')
                plt.title(f'Most Common Keywords{" - " + brand_name if brand_name else ""}')
                
                plot_path = os.path.join(self.output_dir, f'keywords_wordcloud_{brand_name or "all"}.png')
                plt.savefig(plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                saved_plots['keywords_wordcloud'] = plot_path
            
        except Exception as e:
            self.logger.error(f"Error generating visualizations: {e}")
        
        return saved_plots
    
    def create_dashboard_data(self, brand_reviews: Dict[str, List[Dict]]) -> Dict:
        """Create data structure for dashboard visualization"""
        dashboard_data = {
            'summary': {},
            'brand_comparison': {},
            'platform_analysis': {},
            'sentiment_trends': {},
            'top_keywords': {}
        }
        
        all_reviews = []
        for brand, reviews in brand_reviews.items():
            all_reviews.extend(reviews)
        
        if not all_reviews:
            return dashboard_data
        
        df = pd.DataFrame(all_reviews)
        
        # Overall summary
        dashboard_data['summary'] = {
            'total_reviews': len(all_reviews),
            'total_brands': len(brand_reviews),
            'avg_rating': df['rating'].mean(),
            'avg_sentiment': df['sentiment_score'].mean(),
            'platforms': df['platform'].unique().tolist(),
            'countries': df['country'].unique().tolist()
        }
        
        # Brand comparison
        brand_stats = df.groupby('brand').agg({
            'rating': ['count', 'mean'],
            'sentiment_score': 'mean'
        }).round(2)
        
        dashboard_data['brand_comparison'] = brand_stats.to_dict()
        
        # Platform analysis
        platform_stats = df.groupby('platform').agg({
            'rating': ['count', 'mean'],
            'sentiment_score': 'mean'
        }).round(2)
        
        dashboard_data['platform_analysis'] = platform_stats.to_dict()
        
        # Top keywords across all brands
        all_keywords = []
        for review in all_reviews:
            keywords = review.get('keywords', [])
            all_keywords.extend(keywords)
        
        from collections import Counter
        keyword_freq = Counter(all_keywords)
        dashboard_data['top_keywords'] = keyword_freq.most_common(20)
        
        return dashboard_data
    
    def export_complete_dataset(self, brand_reviews: Dict[str, List[Dict]], filename: str = None) -> Dict[str, str]:
        """Export complete dataset with all brands"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brand_reviews_dataset_{timestamp}"
        
        # Combine all reviews
        all_reviews = []
        for brand, reviews in brand_reviews.items():
            all_reviews.extend(reviews)
        
        # Save main dataset
        saved_files = self.save_reviews(all_reviews, filename)
        
        # Save brand summary
        summary_df = self.create_brand_summary(all_reviews)
        if not summary_df.empty:
            summary_path = os.path.join(self.output_dir, f"{filename}_summary.csv")
            summary_df.to_csv(summary_path, index=False)
            saved_files['summary'] = summary_path
        
        # Save dashboard data
        dashboard_data = self.create_dashboard_data(brand_reviews)
        dashboard_path = os.path.join(self.output_dir, f"{filename}_dashboard.json")
        with open(dashboard_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2, default=str)
        saved_files['dashboard'] = dashboard_path
        
        # Generate visualizations
        plots = self.generate_visualizations(all_reviews)
        saved_files.update(plots)
        
        self.logger.info(f"Complete dataset exported with {len(all_reviews)} reviews")
        return saved_files