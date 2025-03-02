import requests

class CoinGeckoAPI:
    """CoinGecko API クライアント"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"

    def get_global_market_data(self):
        """仮想通貨市場全体のデータを取得"""
        url = f"{self.BASE_URL}/global"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"CoinGecko APIエラー: {response.status_code}")

    def get_market_chart(self):
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "30",  # 30日間のデータ
            "interval": "daily"  # 日次データ
        }


    def get_btc_dominance(self):
        """BTCドミナンス（市場支配率）を取得"""
        data = self.get_global_market_data()
        return data["data"]["market_cap_percentage"]["btc"]

    def get_market_cap(self, coin_id="bitcoin"):
        """指定した通貨の時価総額を取得"""
        url = f"{self.BASE_URL}/coins/markets"
        params = {
            "vs_currency": "usd",
            "ids": coin_id
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            market_data = response.json()
            if market_data:
                return market_data[0]["market_cap"]
            else:
                raise ValueError("通貨IDが正しくありません。")
        else:
            raise Exception(f"CoinGecko APIエラー: {response.status_code}")
