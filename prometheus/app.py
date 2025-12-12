from flask import Flask, jsonify
import requests
import json
import time
from threading import Thread, Event
from prometheus_client import Gauge, generate_latest
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
usdt_vnd_gauge = Gauge('usdt_vnd_rate', 'USDT to VND exchange rate from Binance P2P')
last_update_gauge = Gauge('usdt_vnd_last_update', 'Last update timestamp')
fetch_errors = Gauge('usdt_vnd_fetch_errors_total', 'Total number of fetch errors')

# Global state
current_rate = 0
stop_event = Event()

def fetch_usdt_vnd():
    """Fetch USDT/VND rate from Binance P2P API"""
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'vi,vi-VN;q=0.9,en;q=0.8',
        'C2CType': 'c2c_web',
        'ClientType': 'web',
        'Content-Type': 'application/json',
        'Lang': 'vi',
        'Origin': 'https://p2p.binance.com',
        'Referer': 'https://p2p.binance.com/trade/sell/USDT?fiat=VND&payment=all-payments',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    
    payload = {
        "fiat": "VND",
        "page": 1,
        "rows": 3,
        "tradeType": "SELL",
        "asset": "USDT",
        "countries": ["VN"],
        "proMerchantAds": False,
        "shieldMerchantAds": False,
        "filterType": "all",
        "additionalKycVerifyFilter": 0,
        "publisherType": None,
        "payTypes": [],
        "classifies": ["mass", "profession"],
        "transAmount": 10000000
    }
    
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract prices and calculate average
        prices = [float(item["adv"]["price"]) for item in data.get("data", [])]
        
        if prices:
            avg_price = round(sum(prices) / len(prices), 2)
            logger.info(f"Fetched USDT/VND rate: {avg_price}")
            return avg_price
        else:
            logger.warning("No price data available")
            return None
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        fetch_errors.inc()
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        fetch_errors.inc()
        return None
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Error parsing response: {e}")
        fetch_errors.inc()
        return None

def update_loop():
    """Background thread to update exchange rate periodically"""
    global current_rate
    
    # Initial fetch
    logger.info("Starting initial rate fetch...")
    rate = fetch_usdt_vnd()
    if rate:
        current_rate = rate
        usdt_vnd_gauge.set(current_rate)
        last_update_gauge.set(time.time())
    
    # Update loop
    while not stop_event.is_set():
        # Wait for 10 minutes or until stop event
        if stop_event.wait(timeout=600):  # 600 seconds = 10 minutes
            break
        
        rate = fetch_usdt_vnd()
        if rate:
            current_rate = rate
            usdt_vnd_gauge.set(current_rate)
            last_update_gauge.set(time.time())

# Start background thread
update_thread = Thread(target=update_loop, daemon=True)
update_thread.start()

@app.route('/')
def get_average_price():
    """Return current USDT/VND rate as JSON"""
    return jsonify({
        'USDT/VND': current_rate,
        'timestamp': time.time()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'rate': current_rate}), 200

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    # Don't use debug=True in production
    app.run(host='0.0.0.0', port=5000, debug=False)