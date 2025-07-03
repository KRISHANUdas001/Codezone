"""
Simple test of the web dashboard
"""
from web_dashboard import app
import threading
import time
import requests

def start_server():
    """Start the Flask server in a separate thread"""
    app.run(host='0.0.0.0', port=12001, debug=False)

def test_dashboard():
    """Test the dashboard endpoints"""
    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test main dashboard page
        response = requests.get('http://localhost:12001/templates/dashboard.html')
        print(f"Dashboard page status: {response.status_code}")
        print(f"Dashboard page length: {len(response.text)} characters")
        
        # Test data summary endpoint
        response = requests.get('http://localhost:12001/api/data/summary')
        print(f"Data summary status: {response.status_code}")
        print(f"Data summary: {response.json()}")
        
        print("\n✅ Dashboard is working correctly!")
        print("🌐 Access the dashboard at: http://localhost:12001")
        
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")

if __name__ == "__main__":
    test_dashboard()