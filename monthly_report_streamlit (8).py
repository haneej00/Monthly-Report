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
    df24.columns = df24.columns.str.strip().str.lower()
    df25.columns = df25.columns.str.strip().str.lower()
    return df24, df25

df24, df25 = load_data()

# ISO 설명 딕셔너리
iso_dict = {
    111: "LA", 112: "HQ", 121: "OCK", 122: "OCV", 123: "San Jose",
    124: "Seattle", 125: "New York", 126: "Virginia", 128: "Georgia",
    130: "El Monte", 131: "New Jersey", 132: "MM", 133: "Houston",
    135: "San Francisco", 138: "Hawaii", 139: "Chicago", 140: "South Bay",
    143: "GABS", 146: "Dallas", 147: "CRD", 153: "Torrance", 300: "Business Partners"
}

# 계정 유형 정리 함수
def filter_and_classify(df):
    df = df.copy()
    df['account_category'] = df['accounttype'].apply(
        lambda x: 'New account' if str(x).strip().lower() in ['new', 'conversion'] else str(x).strip())
    return df

# 적용
df24 = filter_and_classify(df24)
df25 = filter_and_classify(df25)

# ISO 드롭다운 라벨 만들기
iso_ids = sorted(set(df24['iso'].unique()) | set(df25['iso'].unique()))
iso_labels = [f"{i} - {iso_dict.get(i, str(i))}" for i in iso_ids]
iso_labels.insert(0, "Total")
selected_label = st.selectbox("🔍 Choose ISO", iso_labels)

if selected_label == "Total":
    selected_iso = "Total"
else:
    selected_iso = int(selected_label.split(" - ")[0])

# 피벗 함수 (account count 기준)
def prepare_pivot_count(df24, df25):
    df24_grouped = df24.groupby(['iso', 'account_category']).size().reset_index(name='count')
    df24_grouped['year'] = 2024

    df25_grouped = df25.groupby(['iso', 'account_category']).size().reset_index(name='count')
    df25_grouped['year'] = 2025

    merged = pd.concat([df24_grouped, df25_grouped], ignore_index=True)
    return merged

pivot_count = prepare_pivot_count(df24, df25)

# 차트 + 테이블 출력 함수
def plot_yoy_chart(df, iso, value_label):
    if iso == "Total":
        temp = df.copy()
        label = "All ISOs"
    else:
        temp = df[df['iso'] == iso].copy()
        label = iso_dict.get(iso, str(iso))

    fig = px.bar(
        temp,
        x='account_category',
        y='count',
        color='year',
        barmode='group',
        title=f"{value_label} - {label}",
        labels={'account_category': 'Account Type'}
    )

    fig.update_layout(
        height=400,
        xaxis_tickangle=-15,
        title_font_size=16
    )

    st.plotly_chart(fig, use_container_width=True)

    # 테이블 형식: 행 = 연도, 열 = account type
    table_df = temp.pivot_table(index='year', columns='account_category', values='count', aggfunc='sum').fillna(0).astype(int)
    st.markdown("### 📊 Data Table")
    st.dataframe(table_df, use_container_width=True)

# 출력
st.subheader("📈 Account Count (YOY)")
plot_yoy_chart(pivot_count, selected_iso, "Number of Accounts")
