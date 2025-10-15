import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def render_predict_summary(st, predict):
    buy = predict["buy"].iloc[-1]
    sell = predict["sell"].iloc[-1]
    price = predict["predict_price"].iloc[-1]

    trend = "neutral"
    if abs(buy) > abs(sell):
        trend = "up"
    elif abs(sell) > abs(buy):
        trend = "down"

    label_map = {
        "up": "📈 上げ相場予測",
        "down": "📉 下げ相場予測",
        "neutral": "⏸ 保留"
    }

    label = "保留"
    st.metric(
        label=label_map[trend],
        value=f"{int(price):,}",
        delta=f"{(buy if abs(buy) > abs(sell) else sell):.4f}"
    )

def render_candle_with_predict(st, df, trans):
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    fig.add_trace(
        go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="ローソク足"),
        row=1, col=1
    )

    buy_signal = [x if x > 0.5 else None for x in df["buy"]]
    sell_signal = [x if x < -0.5 else None for x in df["sell"]]

    traces = [
        go.Scatter(x=df["date"], y=buy_signal, mode="markers", name="buy_signal", marker=dict(color="blue", size=10, symbol="triangle-up")),
        go.Scatter(x=df["date"], y=sell_signal, mode="markers", name="sell_signal", marker=dict(color="orange", size=10, symbol="triangle-down"))
    ]
    for t in traces:
        fig.add_trace(t, row=2, col=1)

    for order in trans['open_orders']:

        fig.add_shape(
            type="line",
            x0=df["date"].iloc[0],
            x1=df["date"].iloc[-1],
            y0=order['price'],
            y1=order['price'],
            line=dict(color="#FFD700", width=2, dash="dot"),
            xref="x", yref="y"
        )

    #-------TODO 売買ライン
    """     buy_date = df["date"].iloc[22]
    sell_date = df["date"].iloc[37]
    buy_price = df["close"].iloc[22]
    sell_price = df["close"].iloc[37]

    fig.add_annotation(
        x=sell_date, y=sell_price,
        ax=buy_date, ay=buy_price,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3,
        arrowcolor="green" if sell_price > buy_price else "red",
        arrowsize=1.5, arrowwidth=2
    ) """
    #-------TODO 売買ライン



    fig.update_layout(title="予測データ", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
