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

# 2_evaluate
def fetch_predictions():
    response = requests.get(f"{settings.API_BASE}/api/ml/evaluate/predictions")
    if response.status_code == 200:
        return response.json()
    else:
        return None

# 9_config
def load_config():
    response = requests.get(f"{settings.API_BASE}/api/config")
    if response.status_code == 200:
        return response.json()

def save_config(config):
    return requests.post(f"{settings.API_BASE}/api/config", json=config)
