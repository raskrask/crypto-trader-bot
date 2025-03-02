import ccxt
import json
from config.settings import settings
from config.config_manager import get_config_manager

class CoinCheckAPI:

    def __init__(self):
        self.client = ccxt.coincheck({
            'apiKey': settings.COINCHECK_API_KEY,
            'secret': settings.COINCHECK_API_SECRET
        })
        self.config_data = get_config_manager().get_config()
        self.market = self.config_data.get("market_symbol")

    def get_balance(self):
        balance = self.client.fetch_balance()
        market_symbol = self.market.split("_")
        #return { x: float(balance["info"][x]) for x in market_symbol }
        return [ float(balance["info"][x]) for x in market_symbol ]

    def create_limit_order(self, side, amount, price):
        # 指値注文を出す
        return self.client.create_order(self.market, "limit", side, amount, price)
    
    def create_market_order(self, side, amount):
        # 成行注文を出す
        return self.client.create_order(self.market, "market", side, amount)
    
    def get_trade_history(self, market):
        trades = self.client.fetch_my_trades(market)
        return trades

    def get_open_orders(self, market):
        open_orders = self.client.fetch_open_orders(market)

    def get_cancel_order(self, order_id, market):
        cancel_response = self.client.cancel_order(order_id, market)
        print(cancel_response)

    def get_order_book(self):
        """
        asks: 売り注文の情報
        bids: 買い注文の情報
        """
        response = self.client.publicGetOrderBooks()
        return response

    def get_exchange_rate(self, pair, order_type, amount):
        """
        Coincheck の交換レートを取得
        :param pair: 取引ペア ("btc_jpy" など)
        :param order_type: "buy" または "sell"
        :param amount: 交換する数量
        """
        response = self.client.publicGetExchangeOrdersRate({'pair': pair, 'order_type': order_type, 'amount': amount})
        return response

    def get_latest_rate(self, pair):
        """
        Coincheck の最新レートを取得
        :param pair: 取引ペア ("btc_jpy" など)
        """
        response = self.client.publicGetRatePair({'pair': pair})
        return response

    def get_avg_cost(self):
        """過去の取引履歴から加重平均購入価格を算出"""
        trades = self.client.fetch_my_trades(self.market)

        total_cost = sum(trade["price"] * trade["amount"] for trade in trades)
        total_amount = sum(trade["amount"] for trade in trades)

        if total_amount == 0:
            print("購入数量がゼロのため、加重平均価格を計算できません。")
            return None

        weighted_avg_price = total_cost / total_amount  # 加重平均価格
        return weighted_avg_price

if __name__ == "__main__":
    cc = CoinCheckAPI()
    print(json.dumps(cc.get_balance(), indent=2, ensure_ascii=False))

    print(cc.get_trade_history("btc_jpy"))
    print(cc.get_open_orders("btc_jpy"))
    print(cc.get_order_book())
    books = cc.get_order_book()
    print(books["asks"][0][0], books["bids"][0][0])
    print(books["asks"][-1][0], books["bids"][-1][0])
    print((float(books["asks"][0][0]) + float(books["asks"][-1][0])) / 2, (float(books["bids"][0][0]) + float(books["bids"][-1][0])) / 2 )
    # 例: BTC/JPY の 0.01 BTC を買う場合のレート
    rate_info = cc.get_exchange_rate("btc_jpy", "buy", 0.002)
    print(rate_info)
    rate_info = cc.get_exchange_rate("btc_jpy", "sell", 0.002)
    print(rate_info)

    # 例: BTC/JPY の最新レートを取得
    latest_rate = cc.get_latest_rate("btc_jpy")
    print(latest_rate)

    avg_cost = cc.get_avg_cost()
    print(avg_cost)

#    order = cc.create_limit_order("sell", 0.001, 14539794.0)

#    order = cc.create_limit_order("sell", 0.001, books["bids"][0][0])
#    print(avg_cost)
