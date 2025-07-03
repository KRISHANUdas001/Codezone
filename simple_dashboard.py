#!/usr/bin/env python3
"""
Simple Web Dashboard for Brand Review Scraper
Demonstrates the web interface functionality
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Sample data for demonstration
SAMPLE_DATA = [
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
        'sentiment_score': 0.539,
        'sentiment_label': 'positive',
        'keywords': 'iphone, great, experience, new, camera'
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
        'sentiment_score': -0.367,
        'sentiment_label': 'negative',
        'keywords': 'customer, service, product, okay, terrible'
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
        'sentiment_score': 0.625,
        'sentiment_label': 'positive',
        'keywords': 'samsung, galaxy, fantastic, android, phone'
    }
]

# HTML Template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Brand Review Scraper Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        .reviews-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .reviews-table th,
        .reviews-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .reviews-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .reviews-table tr:hover {
            background-color: #f8f9fa;
        }
        .sentiment-positive {
            color: #28a745;
            font-weight: bold;
        }
        .sentiment-negative {
            color: #dc3545;
            font-weight: bold;
        }
        .rating {
            color: #ffc107;
            font-weight: bold;
        }
        .platform-badge {
            background: #007bff;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
        }
        .country-flag {
            font-weight: bold;
            color: #6c757d;
        }
        .keywords {
            font-style: italic;
            color: #6c757d;
            font-size: 0.9em;
        }
        .refresh-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #218838;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #6c757d;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Brand Review Scraper Dashboard</h1>
        
        <button class="refresh-btn" onclick="refreshData()">🔄 Refresh Data</button>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-reviews">{{ stats.total_reviews }}</div>
                <div class="stat-label">Total Reviews</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-brands">{{ stats.total_brands }}</div>
                <div class="stat-label">Brands Tracked</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-rating">{{ "%.2f"|format(stats.avg_rating) }}</div>
                <div class="stat-label">Average Rating</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="avg-sentiment">{{ "%.3f"|format(stats.avg_sentiment) }}</div>
                <div class="stat-label">Average Sentiment</div>
            </div>
        </div>

        <h2>📊 Recent Reviews</h2>
        <table class="reviews-table">
            <thead>
                <tr>
                    <th>Brand</th>
                    <th>Platform</th>
                    <th>Country</th>
                    <th>Rating</th>
                    <th>Review</th>
                    <th>Sentiment</th>
                    <th>Keywords</th>
                </tr>
            </thead>
            <tbody id="reviews-tbody">
                {% for review in reviews %}
                <tr>
                    <td><strong>{{ review.brand }}</strong></td>
                    <td><span class="platform-badge">{{ review.platform }}</span></td>
                    <td><span class="country-flag">{{ review.country }}</span></td>
                    <td><span class="rating">{{ review.rating }}⭐</span></td>
                    <td>{{ review.review_text[:100] }}{% if review.review_text|length > 100 %}...{% endif %}</td>
                    <td><span class="sentiment-{{ review.sentiment_label }}">{{ review.sentiment_label }} ({{ "%.3f"|format(review.sentiment_score) }})</span></td>
                    <td><span class="keywords">{{ review.keywords }}</span></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="footer">
            <p>🎯 Brand Review Scraper - Real-time Customer Sentiment Analysis</p>
            <p>Last updated: <span id="last-updated">{{ timestamp }}</span></p>
        </div>
    </div>

    <script>
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    // Update stats
                    document.getElementById('total-reviews').textContent = data.stats.total_reviews;
                    document.getElementById('total-brands').textContent = data.stats.total_brands;
                    document.getElementById('avg-rating').textContent = data.stats.avg_rating.toFixed(2);
                    document.getElementById('avg-sentiment').textContent = data.stats.avg_sentiment.toFixed(3);
                    
                    // Update timestamp
                    document.getElementById('last-updated').textContent = data.timestamp;
                    
                    // Update table
                    const tbody = document.getElementById('reviews-tbody');
                    tbody.innerHTML = '';
                    data.reviews.forEach(review => {
                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td><strong>${review.brand}</strong></td>
                            <td><span class="platform-badge">${review.platform}</span></td>
                            <td><span class="country-flag">${review.country}</span></td>
                            <td><span class="rating">${review.rating}⭐</span></td>
                            <td>${review.review_text.substring(0, 100)}${review.review_text.length > 100 ? '...' : ''}</td>
                            <td><span class="sentiment-${review.sentiment_label}">${review.sentiment_label} (${review.sentiment_score.toFixed(3)})</span></td>
                            <td><span class="keywords">${review.keywords}</span></td>
                        `;
                    });
                })
                .catch(error => {
                    console.error('Error refreshing data:', error);
                    alert('Error refreshing data. Please try again.');
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Main dashboard page"""
    df = pd.DataFrame(SAMPLE_DATA)
    
    stats = {
        'total_reviews': len(df),
        'total_brands': df['brand'].nunique(),
        'avg_rating': df['rating'].mean(),
        'avg_sentiment': df['sentiment_score'].mean()
    }
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        reviews=SAMPLE_DATA,
        stats=stats,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/api/data')
def api_data():
    """API endpoint for dashboard data"""
    df = pd.DataFrame(SAMPLE_DATA)
    
    stats = {
        'total_reviews': len(df),
        'total_brands': df['brand'].nunique(),
        'avg_rating': df['rating'].mean(),
        'avg_sentiment': df['sentiment_score'].mean()
    }
    
    return jsonify({
        'reviews': SAMPLE_DATA,
        'stats': stats,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/brands')
def api_brands():
    """Get brand statistics"""
    df = pd.DataFrame(SAMPLE_DATA)
    brand_stats = df.groupby('brand').agg({
        'rating': ['count', 'mean'],
        'sentiment_score': 'mean',
        'helpful_votes': 'sum'
    }).round(3)
    
    brand_stats.columns = ['review_count', 'avg_rating', 'avg_sentiment', 'total_helpful_votes']
    brand_stats = brand_stats.reset_index()
    
    return jsonify(brand_stats.to_dict('records'))

if __name__ == '__main__':
    print("🚀 Starting Simple Brand Review Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:9000")
    print("🔗 API endpoints:")
    print("   - /health - Health check")
    print("   - /api/data - Dashboard data")
    print("   - /api/brands - Brand statistics")
    
    app.run(host='0.0.0.0', port=9000, debug=False)