import streamlit as st
import pandas as pd
import plotly.express as px

def show(st, result):

    st.write("モデル評価指標")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Accuracy", f"{result['Accuracy']:.4f}")
    col2.metric("MSE", f"{result['eval_results']['MSE']:.4f}")
    col3.metric("RMSE", f"{result['eval_results']['RMSE']:.4f}")
    col4.metric("MAE", f"{result['eval_results']['MAE']:.4f}")
    col5.metric("R² Score", f"{result['eval_results']['R2 Score']:.3f}")

    # 辞書を DataFrame に変換
    data = result["importance"]
    importance_df = pd.DataFrame({
        "Feature": list(data["Feature"].values()),
        "Importance": list(data["Importance"].values()),
        "ModelName": list(data["ModelName"].values())
    })
    importance_df = importance_df.sort_values(by="Importance", ascending=False)  # 降順ソート

    # **バーグラフで可視化**
    fig = px.bar(importance_df[:20], x="Importance", y="Feature", orientation="h", color="ModelName",
                title="特徴量重要度（SHAP Top 20）", labels={"Importance": "重要度", "Feature": "特徴量"})
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # Y軸の並び順を修正

    st.plotly_chart(fig, use_container_width=True)

