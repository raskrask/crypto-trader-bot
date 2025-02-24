import streamlit as st
import pandas as pd
import plotly.express as px

def show(st, result):

    # 辞書を DataFrame に変換
    importance_df = pd.DataFrame(result["importance"][0].items(), columns=["Feature", "Importance"])
    importance_df = importance_df.sort_values(by="Importance", ascending=False)  # 降順ソート

    # **バーグラフで可視化**
    fig = px.bar(importance_df[:10], x="Importance", y="Feature", orientation="h",
                title="特徴量重要度（SHAP Top 10）", labels={"Importance": "重要度", "Feature": "特徴量"})
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # Y軸の並び順を修正

    st.plotly_chart(fig, use_container_width=True)

    st.write("モデル評価指標")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MSE", f"{result['eval_results']['MSE']:.4f}")
    col2.metric("RMSE", f"{result['eval_results']['RMSE']:.4f}")
    col3.metric("MAE", f"{result['eval_results']['MAE']:.4f}")
    col4.metric("R² Score", f"{result['eval_results']['R2 Score']:.3f}")
