from config.config_manager import get_config_manager

def market_symbol(symbol: str = None, fmt: str = "raw", prefix: str = None) -> str:
    """
    市場シンボル（例: btc_jpy）を用途に応じてフォーマット変換する。

    Args:
        symbol (str): 例 "btc_jpy", "eth_usdt"
        fmt (str): 出力形式を指定
            - "raw": 元の形式（デフォルト）
            - "ccxt": "BTC/JPY" 形式（大文字+スラッシュ）
            - "base": "BTC" のみ
            - "quote": "JPY" のみ

    Returns:
        str: 指定形式のシンボル文字列
    """
    if not symbol:
        config_data = get_config_manager().get_config()
        symbol = config_data.get("market_symbol")

    parts = symbol.lower().split("_")
    if len(parts) != 2:
        raise ValueError(f"Invalid market symbol format: {symbol}")

    base, quote = parts[0].upper(), parts[1].upper()

    if fmt == "raw":
        return f"{prefix}{symbol.lower()}"
    elif fmt == "ccxt":
        return f"{base}/{quote}"
    elif fmt == "base":
        return base
    elif fmt == "quote":
        return quote
    else:
        raise ValueError(f"Unsupported format: {fmt}")
