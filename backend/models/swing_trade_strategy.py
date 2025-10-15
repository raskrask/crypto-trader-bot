import numpy as np
from utils.market_symbol import market_symbol

class SwingTradeStrategy:
    def __init__(self, data):
        """
        スイングトレード戦略の基礎クラス。
        :param data: 過去の価格データ (OHLCV: Open, High, Low, Close, Volume)
        """
        self.data = data

    def trend_following(self):
        """
        トレンドフォロー戦略（順張り）。
        - 移動平均線（SMA, EMA）を活用
        - RSIやMACDを組み合わせ、トレンド方向を判断
        """

        columns = []
        columns += self._add_ma_cross_signals()
        columns += self._add_candle_signals()
        columns += self._add_rsi_triple_reversal_signals()        

        return columns

    def range_trading(self):
        """
        レンジトレード戦略。
        - ボリンジャーバンドやサポート・レジスタンスを活用
        - RSIを使って買われ過ぎ・売られ過ぎを判断
        """
        pass  # ここにロジックを実装

    def breakout_strategy(self):
        """
        ブレイクアウト戦略。
        - 価格が一定のレンジを超えたらエントリー
        - ATR（平均真実幅）を利用してボラティリティを考慮
        """
        pass  # ここにロジックを実装

    def apply_fundamentals(self):
        """
        ファンダメンタルズ分析を考慮。
        - オンチェーンデータ（取引所流入量、クジラの動き）
        - マクロ経済（米国金利、インフレ率）
        - 市場センチメント（Fear & Greed Index）
        """
        pass  # ここにロジックを実装

    def execute_trade(self):
        """
        売買の判断ロジックを統合し、エントリー・エグジットを決定。
        """
        pass  # ここに統合ロジックを実装


    def _add_ma_cross_signals(self):
        """
        移動平均クロス（短期が長期を上抜け → 買いシグナル候補）
        売りシグナル：逆クロス OR 将来利回りが-閾値以下
        """
        df = self.data.copy()
        columns = []
        sma_keys = [int(col.split("_")[1]) for col in df.columns if col.startswith("sma_")]
        sma_keys = sorted(sma_keys)
        for period_1 in sma_keys:
            for period_2 in sma_keys:
                if period_1 < period_2:
                    df_period_1 = df[f"sma_{period_1}"]
                    df_period_2 = df[f"sma_{period_2}"]
                    df[f"ma_cross_up_{period_1}_{period_2}"] = ((df_period_1 > df_period_2) & (df_period_1.shift(1) <= df_period_2.shift(1))).astype(int) 
                    df[f"ma_cross_down_{period_1}_{period_2}"] = ((df_period_1 < df_period_2) & (df_period_1.shift(1) >= df_period_2.shift(1))).astype(int) 
                    columns.append(f"ma_cross_up_{period_1}_{period_2}")
                    columns.append(f"ma_cross_down_{period_1}_{period_2}")
        self.data = df
        return columns

    def _add_candle_signals(self):
        """陽線で5MAを上抜け、陰線で下抜けなどのシグナル"""
        df = self.data.copy()
        sma5 = df["sma_5"]
        open = df[market_symbol(prefix="open_")]
        close = df[market_symbol(prefix="close_")]

        # 陽線で5MAを上抜け
        df["candle_cross_up_5"] = ((close > open) & (close > sma5) & (open <= sma5)).astype(int)

        # 陰線で5MAを下抜け
        df["candle_cross_down_5"] = ((close < open) & (close < sma5) & (open >= sma5)).astype(int)

        self.data = df
        return ["candle_cross_up_5", "candle_cross_down_5"]

    def _add_rsi_triple_reversal_signals(self):
        """
        RSIが低水準・高水準で複数回反発／反落したパターンを特徴量として追加。
        - RSIが低水準で10日以内に3回反発 → 売られすぎ圏からの反転が近いと考えられ、押し目買いの好機と判断
        - RSIが高水準で10日以内に3回反落 → 利確／売りシグナル
        """
        df = self.data.copy()

        # RSIの上昇・下落を検出
        df["RSI_diff"] = df["RSI"].diff()
        df["RSI_dir"] = np.sign(df["RSI_diff"])  # +1=上昇, -1=下落

        # --- 反発・反落判定 ---
        low_thresh=35
        # 「前日まで下がっていて、かつRSIが低水準で上昇に転じた」
        df["RSI_rebound"] = (
            (df["RSI"].shift(1) < low_thresh) &  # 前日まで低水準
            (df["RSI_diff"] > 0) &               # 上昇に転じた
            (df["RSI_diff"].shift(1) < 0)        # 直前までは下落中
        ).astype(int)

        # 「前日まで上がっていて、かつRSIが高水準で下落に転じた」
        high_thresh=65
        df["RSI_fall"] = (
            (df["RSI"].shift(1) > high_thresh) &  # 前日まで高水準
            (df["RSI_diff"] < 0) &                # 下落に転じた
            (df["RSI_diff"].shift(1) > 0)         # 直前までは上昇中
        ).astype(int)

        # --- 一定期間内の発生回数 ---
        rsi_period=10
        df["RSI_rebound_count"] = df["RSI_rebound"].rolling(window=rsi_period).sum()
        df["RSI_fall_count"]    = df["RSI_fall"].rolling(window=rsi_period).sum()

        # --- 3回以上で強シグナル ---
        df["RSI_triple_rebound"] = (df["RSI_rebound_count"] >= 3).astype(int)
        df["RSI_triple_fall"]    = (df["RSI_fall_count"] >= 3).astype(int)

        self.data = df
        return ["RSI_triple_rebound", "RSI_triple_fall"]

# データをロードし、戦略を実行する例
if __name__ == "__main__":
    historical_data = None  # 過去データを取得
    strategy = SwingTradeStrategy(historical_data)
    strategy.execute_trade()
