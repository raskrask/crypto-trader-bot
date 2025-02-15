import requests
from config.settings import settings

# 1_training
def train_model(mode, method="GET", data=None):
    url = f"{settings.API_BASE}/api/ml/train/{mode}"
    if method == "POST":
        response = requests.post(url, json=data)
    else:
        response = requests.get(url)
    return response.json()

# 9_config
def load_initial_config():
    response = requests.get(f"{settings.API_BASE}/api/config")
    if response.status_code == 200:
        data = response.json()
        if "message" not in data:
            return data
    return {
        "market_symbol": "BTC/JPY",
        "training_period_months": 3,
        "ensemble_ratio": 0.5,
        "epochs": 50,
        "test_ratio": 0.2
    }

def save_config(config):
    return requests.post(f"{settings.API_BASE}/api/config", json=config)
