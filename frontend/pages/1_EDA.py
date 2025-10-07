import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from config.settings import settings

st.set_page_config(page_title="Explanatory Data Analysis", layout="wide")

st.title("🔍 Explanatory Data Analysis")

# ---------------------------
if st.button("ボックス相場をもとにトレード戦略の有効性"):
    st.markdown(
        """
        - ボックス相場を用いて、抵抗線とサポートラインを特定することで、売買のタイミングを見極める
        - 抵抗線に近づいたら売り、サポートラインに近づいたら買いの戦略を取る
        """,
        unsafe_allow_html=True,
    )
    #        - ボックスの幅が狭い場合は、価格が安定しているため、短期的なトレードが有効
    #        - ボックスの幅が広い場合は、価格変動が大きいため、長期的なトレードが有効
    url = f"{settings.API_BASE}/api/eda/box_market_price "
    res = requests.get(url).json()

    df = pd.DataFrame(res)
    high_points = df[df["high_points"]]
    low_points = df[df["low_points"]]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    traces = [
        go.Candlestick(x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="ローソク足"),
        go.Scatter(x=df["timestamp"], y=df["rolling_max"], mode="lines", name="rolling_max", line=dict(color="blue", width=1)),
        go.Scatter(x=df["timestamp"], y=df["rolling_min"], mode="lines", name="rolling_min", line=dict(color="red", width=1)),
        go.Scatter(x=df["timestamp"], y=df["sma"], mode="lines", name="sma", line=dict(color="yellow", width=1)),
        go.Scatter(x=high_points["timestamp"], y=high_points["high"], mode="markers", name="high_points", marker=dict(color="red", size=8, symbol="circle")),
        go.Scatter(x=low_points["timestamp"], y=low_points["high"], mode="markers", name="low_points", marker=dict(color="green", size=8, symbol="circle"))
    ]

    for t in traces:
        fig.add_trace(t, row=1, col=1)

    # ボックス区間の背景を追加
    in_box = False
    start_idx = None

    for i in range(len(df)):
        if df["in_box"].iloc[i] and not in_box:
            # ボックス開始
            in_box = True
            start_idx = i
        elif (not df["in_box"].iloc[i] or i == len(df) - 1) and in_box:
            # ボックス終了
            in_box = False
            end_idx = i

            fig.add_vrect(
                x0=df["timestamp"].iloc[start_idx], x1=df["timestamp"].iloc[end_idx],
                fillcolor="LightGreen", opacity=0.2, layer="below", line_width=0,
            )

    # 出来高
    high_volume = df[df['is_high_volume']]
    buy_signal = df[df['buy_signal'] == 1]
    sell_signal = df[df['sell_signal'] == 1]

    colors = ["green" if c > o else "red" for c, o in zip(df["close"], df["open"])]
    traces = [
        go.Bar(x=df["timestamp"], y=df["volume"], name="出来高", marker=dict(color=colors)),
        go.Scatter(x=buy_signal["timestamp"], y=buy_signal["buy_signal"]*100, mode="markers", name="buy_signal", marker=dict(color="blue", size=10, symbol="triangle-up")),
        go.Scatter(x=sell_signal["timestamp"], y=sell_signal["sell_signal"]*-100, mode="markers", name="sell_signal", marker=dict(color="orange", size=10, symbol="triangle-down"))
    ]
    for t in traces:
        fig.add_trace(t, row=2, col=1)

    fig.update_layout(title="ローソク足 + ボックス背景", xaxis_rangeslider_visible=False)

    fig.update_layout(title=f"ローソク足チャート", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)


# ---------------------------
if st.button("直近2〜3か月の急増出来高日と価格比較"):
    st.markdown(
        """
        - 過去の「出来高急増日」に注目し、その日に取引した人がまだ保有していると仮定
        - 現在の価格と当時の高値・安値を比較し、投資家の含み損・含み益の傾向を把握する
        """,
        unsafe_allow_html=True,
    )

    url = f"{settings.API_BASE}/api/eda/box_market_price "
    res = requests.get(url).json()

    df = pd.DataFrame(res)
    high_points = df[df["high_points"]]
    low_points = df[df["low_points"]]

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
    traces = [
        go.Candlestick(x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="ローソク足"),
        go.Scatter(x=df["timestamp"], y=df["sma"], mode="lines", name="sma", line=dict(color="yellow", width=1)),
        go.Scatter(x=high_points["timestamp"], y=high_points["high"], mode="markers", name="high_points", marker=dict(color="red", size=8, symbol="circle")),
        go.Scatter(x=low_points["timestamp"], y=low_points["high"], mode="markers", name="low_points", marker=dict(color="green", size=8, symbol="circle"))
    ]

    for t in traces:
        fig.add_trace(t, row=1, col=1)

    # 出来高
    high_volume = df[df['is_high_volume']]
    colors = ["green" if c > o else "red" for c, o in zip(df["close"], df["open"])]
    traces = [
        go.Bar(x=df["timestamp"], y=df["volume"], name="出来高", marker=dict(color=colors)),
        go.Scatter(x=high_volume["timestamp"], y=high_volume["volume"], mode="markers", name="high_volume", marker=dict(color="red", size=8, symbol="circle"))
    ]
    for t in traces:
        fig.add_trace(t, row=2, col=1)

    for idx, row in high_volume.iterrows():
        start_date = row["timestamp"]
        end_date = pd.to_datetime(start_date) + pd.Timedelta(days=90)  # 3か月後
        fig.add_shape(
            type="rect",
            x0=start_date,
            x1=end_date,
            y0=row["low"],   # 縦軸下限 = その日の安値
            y1=row["high"],  # 縦軸上限 = その日の高値
            line=dict(color="red", width=1),
            fillcolor="red",
            opacity=0.2,
            layer="below"
        )

    fig.update_layout(title="出来高", xaxis_rangeslider_visible=False)

    fig.update_layout(title=f"出来高チャート", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)


# ---------------------------
if False:  # st.button("WIP 仮説：アルトコインとBTCの相関関係"):

    st.markdown(
        """
        ### 仮説
        アルトコインを売買対象通貨としたときに、BTCが仮想通貨市場全体に大きな影響を与えるため、BTCとの強い相関関係があると考えられる。
        | BTC時価総額 | BTCドミナンス | 市場の傾向 |
        | ---- | ---- | ---- |
        | 上昇 | 上昇 | BTCに資金が集中（安全資産として買われる）|
        | 上昇 | 下降 | BTCとともにアルトコインも上昇（アルトシーズン）|
        | 下降 | 上昇 | 投資家がアルトコインからBTCへ資金移動（アルト売り）|
        | 下降 | 下降 | 仮想通貨市場全体が下落（リスク回避でUSDTや法定通貨へ逃避）|
        """,
        unsafe_allow_html=True,
    )

    url = f"{settings.API_BASE}/api/eda/explore"
    response = requests.get(url)
    st.write(response.json())

    df_vite = pd.DataFrame(response.json()["VITE/USDT"])
    df_btc = pd.DataFrame(response.json()["BTC/USDT"])

    # 2列のカラムを作成
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"### VITE/USDT の 1日足データ")
        st.dataframe(df_vite)

    with col2:
        st.write(f"### Close価格の推移をグラフ化")
        # st.line_chart(df_vite.set_index("timestamp")["close"])
        # st.line_chart(df_btc.set_index("timestamp")["close"])

        df = pd.DataFrame({
            "日付": pd.to_datetime(df_vite["timestamp"]),
            "VITE/USDT": df_vite["close"],
            "BTC/USDT": df_btc["close"],
        })

        st.subheader("📊 VITE, BTCの指定日の比較")
        fig = px.line(
            df,
            x="日付",
            y=["VITE/USDT", "BTC/USDT"],
            labels={
                "value": "価格",
                "variable": "データ"
            },
        )
        fig.update_layout(yaxis=dict(range=[80000, 120000]))
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        # ローソク足チャート
        fig = go.Figure(data=[go.Candlestick(
            x=df_vite["timestamp"],
            open=df_vite["open"],
            high=df_vite["high"],
            low=df_vite["low"],
            close=df_vite["close"],
        )])
        fig.update_layout(title=f"VITE/USDT ローソク足チャート", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig)  # Streamlitで表示

    with col4:
        # ボックスプロット
        fig = px.box(df_vite, y="close", title=f"VITE/USDT の価格分布")
        st.plotly_chart(fig)

# if False:  # st.button("WIP 仮説：アルトコインとBTCの相関関係"):

# ---------------------------
if (False):  # st.button("WIP 仮説：スイングトレードは短期ノイズを排除し、精度の高い予測が可能になる"):
    st.markdown(
        """
        ### 仮説
        - 短期のノイズに左右されないため、**移動平均線（SMA）やRSI** などの指標が機能しやすい
        - 短期の小さな値動きを狙う **スキャルピングやデイトレード** は、ボラティリティが高いとリスクも大きくなる
        - **スイングトレード** は、長期間の値動きを捉えられるため、ボラティリティが高い相場でもリスクを分散しやすい

        ---
        ### **スキャルピング vs. デイトレード vs. スイングトレード**
        | 評価項目 | スキャルピング | デイトレード | スイングトレード |
        | ---- | ---- | ---- | ---- |
        | **ROI** | 低～中 | 中～高 | 高 |
        | **勝率** | 50%～60% | 60%～70% | 50%～65% |
        | **手数料影響** | 大 | 中 | 小 |
        | **ストレス** | 高 | 中 | 低 |
        | **適した市場状況** | 高ボラティリティ | 中程度のトレンド | 長期トレンド |
        """,
        unsafe_allow_html=True,
    )

if False:  # st.button("WIP OpenAIを使ってトレンドの転換点を正確に捉えられるか？"):
    pass

if False:  # st.button("WIP ボラティリティ予測が可能か？"):
    st.markdown("予測結果のMSEやRMSEを算出し、精度を評価する")
