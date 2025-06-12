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

@app.route('/templates/dashboard.html')
def dashboard_template():
    """Serve dashboard template"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Review Scraper Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .chart-container { margin: 20px 0; }
        .loading { text-align: center; padding: 20px; }
        .brand-tag { display: inline-block; margin: 2px; padding: 4px 8px; background: #e9ecef; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <h1 class="mt-4 mb-4">Review Scraper Dashboard</h1>
        
        <!-- Scraping Controls -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Start New Scraping Session</h5>
                    </div>
                    <div class="card-body">
                        <form id="scrapingForm">
                            <div class="row">
                                <div class="col-md-3">
                                    <label for="brands" class="form-label">Brands (comma-separated)</label>
                                    <input type="text" class="form-control" id="brands" placeholder="Apple, Samsung, Microsoft">
                                </div>
                                <div class="col-md-3">
                                    <label for="countries" class="form-label">Countries</label>
                                    <select multiple class="form-control" id="countries">
                                        <option value="US" selected>United States</option>
                                        <option value="UK" selected>United Kingdom</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label for="platforms" class="form-label">Platforms</label>
                                    <select multiple class="form-control" id="platforms">
                                        <option value="trustpilot" selected>Trustpilot</option>
                                        <option value="google_reviews">Google Reviews</option>
                                        <option value="amazon">Amazon</option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label for="maxReviews" class="form-label">Max Reviews per Brand</label>
                                    <input type="number" class="form-control" id="maxReviews" value="20" min="1" max="100">
                                </div>
                                <div class="col-md-1">
                                    <label class="form-label">&nbsp;</label>
                                    <button type="submit" class="btn btn-primary form-control">Start Scraping</button>
                                </div>
                            </div>
                        </form>
                        <div id="scrapingStatus" class="mt-3"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Data Summary -->
        <div class="row mb-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Data Summary</h5>
                    </div>
                    <div class="card-body">
                        <div id="dataSummary">Loading...</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Visualizations -->
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Rating Distribution</h5>
                    </div>
                    <div class="card-body">
                        <div id="ratingChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Brand Comparison</h5>
                    </div>
                    <div class="card-body">
                        <div id="brandChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h5>Platform Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div id="platformChart" class="chart-container"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Load initial data
        loadDataSummary();
        loadCharts();
        
        // Handle scraping form submission
        document.getElementById('scrapingForm').addEventListener('submit', function(e) {
            e.preventDefault();
            startScraping();
        });
        
        function startScraping() {
            const brands = document.getElementById('brands').value.split(',').map(b => b.trim()).filter(b => b);
            const countries = Array.from(document.getElementById('countries').selectedOptions).map(o => o.value);
            const platforms = Array.from(document.getElementById('platforms').selectedOptions).map(o => o.value);
            const maxReviews = parseInt(document.getElementById('maxReviews').value);
            
            if (brands.length === 0) {
                alert('Please enter at least one brand');
                return;
            }
            
            const statusDiv = document.getElementById('scrapingStatus');
            statusDiv.innerHTML = '<div class="alert alert-info">Scraping in progress... This may take several minutes.</div>';
            
            fetch('/api/scrape', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    brands: brands,
                    countries: countries,
                    platforms: platforms,
                    max_reviews: maxReviews
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
                } else {
                    statusDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
                    // Reload data and charts
                    setTimeout(() => {
                        loadDataSummary();
                        loadCharts();
                    }, 1000);
                }
            })
            .catch(error => {
                statusDiv.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
            });
        }
        
        function loadDataSummary() {
            fetch('/api/data/summary')
                .then(response => response.json())
                .then(data => {
                    const summaryDiv = document.getElementById('dataSummary');
                    if (data.files && data.files.length > 0) {
                        let html = '<h6>Available Files:</h6><ul>';
                        data.files.forEach(file => {
                            html += `<li><a href="/api/download/${file.name}" target="_blank">${file.name}</a> (${(file.size/1024).toFixed(1)} KB)</li>`;
                        });
                        html += '</ul>';
                        summaryDiv.innerHTML = html;
                    } else {
                        summaryDiv.innerHTML = '<p>No data files available. Start a scraping session to generate data.</p>';
                    }
                })
                .catch(error => {
                    document.getElementById('dataSummary').innerHTML = '<p>Error loading data summary</p>';
                });
        }
        
        function loadCharts() {
            // Load rating distribution chart
            fetch('/api/visualizations/rating_distribution')
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        Plotly.newPlot('ratingChart', data.data, data.layout);
                    }
                })
                .catch(error => {
                    document.getElementById('ratingChart').innerHTML = '<p>No data available for rating distribution</p>';
                });
            
            // Load brand comparison chart
            fetch('/api/visualizations/brand_comparison')
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        Plotly.newPlot('brandChart', data.data, data.layout);
                    }
                })
                .catch(error => {
                    document.getElementById('brandChart').innerHTML = '<p>No data available for brand comparison</p>';
                });
            
            // Load platform analysis chart
            fetch('/api/visualizations/platform_analysis')
                .then(response => response.json())
                .then(data => {
                    if (!data.error) {
                        Plotly.newPlot('platformChart', data.data, data.layout);
                    }
                })
                .catch(error => {
                    document.getElementById('platformChart').innerHTML = '<p>No data available for platform analysis</p>';
                });
        }
    </script>
</body>
</html>
    '''

if __name__ == '__main__':
    # Create templates directory and dashboard template
    os.makedirs('templates', exist_ok=True)
    
    app.run(host='0.0.0.0', port=12000, debug=True)