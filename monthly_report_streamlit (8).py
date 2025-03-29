import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(layout="wide")

st.title("📊 YOY Monthly Report Dashboard")

@st.cache_data
def load_data():
    df24 = pd.read_excel("Processed_Approved_202402.xlsx")
    df25 = pd.read_excel("Processed_Approved_202502.xlsx")
    cc24 = pd.read_excel("Processed_Cancellation_202402.xlsx")
    cc25 = pd.read_excel("Processed_Cancellation_202502.xlsx")
    for df in [df24, df25, cc24, cc25]:
        df.columns = df.columns.str.strip().str.lower()
    return df24, df25, cc24, cc25

df24, df25, cc24, cc25 = load_data()

# ISO 설명 딕셔너리
iso_dict = {
    111: "LA", 112: "HQ", 121: "OCK", 122: "OCV", 123: "San Jose",
    124: "Seattle", 125: "New York", 126: "Virginia", 128: "Georgia",
    130: "El Monte", 131: "New Jersey", 132: "MM", 133: "Houston",
    135: "San Francisco", 138: "Hawaii", 139: "Chicago", 140: "South Bay",
    143: "GABS", 146: "Dallas", 147: "CRD", 153: "Torrance", 300: "Business Partners"
}

# ISO 드롭다운 라벨 만들기
iso_ids = sorted(set(df24['iso'].unique()) | set(df25['iso'].unique()) | set(cc24['iso'].unique()) | set(cc25['iso'].unique()))
iso_labels = [f"{i} - {iso_dict.get(i, str(i))}" for i in iso_ids]
iso_labels.insert(0, "Total")
selected_label = st.selectbox("🔍 Choose ISO", iso_labels)

if selected_label == "Total":
    selected_iso = "Total"
else:
    selected_iso = int(selected_label.split(" - ")[0])

# 취소 데이터 요약 함수
def prepare_cancellation_summary(cc24, cc25):
    cc24_grouped = cc24.groupby('iso').agg(
        account_count=('mid', 'count'),
        volume_sum=('monthlyvol', 'sum'),
        profit_sum=('profit', 'sum')
    ).reset_index()
    cc24_grouped['year'] = 2024

    cc25_grouped = cc25.groupby('iso').agg(
        account_count=('mid', 'count'),
        volume_sum=('monthlyvol', 'sum'),
        profit_sum=('profit', 'sum')
    ).reset_index()
    cc25_grouped['year'] = 2025

    return pd.concat([cc24_grouped, cc25_grouped], ignore_index=True)

cancellation_summary = prepare_cancellation_summary(cc24, cc25)

# 취소 시각화 함수
def plot_cancellation_chart(df, iso):
    if iso == "Total":
        temp = df.groupby('year')[['account_count', 'volume_sum', 'profit_sum']].sum().reset_index()
    else:
        temp = df[df['iso'] == iso].copy()

    temp_melted = temp.melt(id_vars='year', var_name='metric', value_name='value')

    fig = px.bar(
        temp_melted,
        x='metric',
        y='value',
        color='year',
        barmode='group',
        text='value',
        color_discrete_map={2024: '#1f77b4', 2025: '#ff7f0e'},
        title="🛑 Cancellation Summary - Accounts, Volume, Profit"
    )

    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, xaxis_tickangle=-15)
    st.plotly_chart(fig, use_container_width=True)

# 출력
st.subheader("📉 Cancellation Overview")
plot_cancellation_chart(cancellation_summary, selected_iso)

# 이하 기존 승인 데이터 시각화 함수들 이어짐...
