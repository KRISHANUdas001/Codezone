"""
Web dashboard for visualizing scraped review data
"""
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime
import plotly.graph_objs as go
import plotly.utils
from collections import Counter

from main_scraper import ReviewScraperOrchestrator
from data_processor import DataProcessor
from sentiment_analyzer import SentimentAnalyzer

app = Flask(__name__)
CORS(app)

# Global variables
scraper = None
data_processor = DataProcessor()
sentiment_analyzer = SentimentAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start scraping process"""
    global scraper
    
    try:
        data = request.get_json()
        brands = data.get('brands', [])
        countries = data.get('countries', ['US', 'UK'])
        platforms = data.get('platforms', ['trustpilot'])
        max_reviews = data.get('max_reviews', 20)
        
        if not brands:
            return jsonify({'error': 'No brands specified'}), 400
        
        # Initialize scraper
        scraper = ReviewScraperOrchestrator(headless=True)
        
        # Start scraping
        saved_files = scraper.run_full_scraping_session(
            brands=brands,
            countries=countries,
            platforms=platforms,
            max_reviews_per_brand=max_reviews
        )
        
        return jsonify({
            'status': 'success',
            'message': f'Scraping completed for {len(brands)} brands',
            'files': saved_files
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/summary')
def get_data_summary():
    """Get summary of available data"""
    try:
        output_dir = 'output'
        files = []
        
        if os.path.exists(output_dir):
            for file in os.listdir(output_dir):
                if file.endswith(('.csv', '.json', '.xlsx')):
                    file_path = os.path.join(output_dir, file)
                    file_info = {
                        'name': file,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    }
                    files.append(file_info)
        
        return jsonify({'files': files})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/data/brands')
def get_brands_data():
    """Get brand comparison data"""
    try:
        # Look for the latest dataset
        output_dir = 'output'
        dashboard_files = [f for f in os.listdir(output_dir) if f.endswith('_dashboard.json')]
        
        if not dashboard_files:
            return jsonify({'error': 'No data available'}), 404
        
        # Get the most recent dashboard file
        latest_file = max(dashboard_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
        
        with open(os.path.join(output_dir, latest_file), 'r') as f:
            dashboard_data = json.load(f)
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/rating_distribution')
def rating_distribution():
    """Generate rating distribution chart"""
    try:
        # Load latest dataset
        output_dir = 'output'
        csv_files = [f for f in os.listdir(output_dir) if f.startswith('brand_reviews_dataset_') and f.endswith('.csv')]
        
        if not csv_files:
            return jsonify({'error': 'No dataset available'}), 404
        
        latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
        df = pd.read_csv(os.path.join(output_dir, latest_file))
        
        # Create rating distribution chart
        rating_counts = df['rating'].value_counts().sort_index()
        
        fig = go.Figure(data=[
            go.Bar(x=rating_counts.index, y=rating_counts.values, name='Reviews')
        ])
        
        fig.update_layout(
            title='Rating Distribution',
            xaxis_title='Rating',
            yaxis_title='Number of Reviews',
            template='plotly_white'
        )
        
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/brand_comparison')
def brand_comparison():
    """Generate brand comparison chart"""
    try:
        # Load latest dataset
        output_dir = 'output'
        csv_files = [f for f in os.listdir(output_dir) if f.startswith('brand_reviews_dataset_') and f.endswith('.csv')]
        
        if not csv_files:
            return jsonify({'error': 'No dataset available'}), 404
        
        latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
        df = pd.read_csv(os.path.join(output_dir, latest_file))
        
        # Create brand comparison chart
        brand_stats = df.groupby('brand').agg({
            'rating': ['mean', 'count'],
            'sentiment_score': 'mean'
        }).round(2)
        
        brands = brand_stats.index.tolist()
        avg_ratings = brand_stats[('rating', 'mean')].tolist()
        review_counts = brand_stats[('rating', 'count')].tolist()
        avg_sentiments = brand_stats[('sentiment_score', 'mean')].tolist()
        
        fig = go.Figure()
        
        # Add average rating bars
        fig.add_trace(go.Bar(
            name='Average Rating',
            x=brands,
            y=avg_ratings,
            yaxis='y',
            offsetgroup=1
        ))
        
        # Add sentiment scores as line
        fig.add_trace(go.Scatter(
            name='Average Sentiment',
            x=brands,
            y=avg_sentiments,
            yaxis='y2',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='Brand Comparison: Ratings and Sentiment',
            xaxis_title='Brand',
            yaxis=dict(title='Average Rating', side='left'),
            yaxis2=dict(title='Average Sentiment', side='right', overlaying='y'),
            template='plotly_white',
            hovermode='x unified'
        )
        
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/visualizations/platform_analysis')
def platform_analysis():
    """Generate platform analysis chart"""
    try:
        # Load latest dataset
        output_dir = 'output'
        csv_files = [f for f in os.listdir(output_dir) if f.startswith('brand_reviews_dataset_') and f.endswith('.csv')]
        
        if not csv_files:
            return jsonify({'error': 'No dataset available'}), 404
        
        latest_file = max(csv_files, key=lambda f: os.path.getmtime(os.path.join(output_dir, f)))
        df = pd.read_csv(os.path.join(output_dir, latest_file))
        
        # Create platform analysis chart
        platform_stats = df.groupby('platform').agg({
            'rating': ['mean', 'count'],
            'sentiment_score': 'mean'
        }).round(2)
        
        platforms = platform_stats.index.tolist()
        avg_ratings = platform_stats[('rating', 'mean')].tolist()
        review_counts = platform_stats[('rating', 'count')].tolist()
        
        fig = go.Figure(data=[
            go.Bar(name='Average Rating', x=platforms, y=avg_ratings),
            go.Bar(name='Review Count', x=platforms, y=review_counts, yaxis='y2')
        ])
        
        fig.update_layout(
            title='Platform Analysis',
            xaxis_title='Platform',
            yaxis=dict(title='Average Rating'),
            yaxis2=dict(title='Review Count', overlaying='y', side='right'),
            barmode='group',
            template='plotly_white'
        )
        
        return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        return send_from_directory('output', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404


if __name__ == '__main__':
    # Create templates directory and dashboard template
    os.makedirs('templates', exist_ok=True)
    
    app.run(host='0.0.0.0', port=12001, debug=True)
