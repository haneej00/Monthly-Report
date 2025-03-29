import streamlit as st
import plotly.express as px
import pandas as pd

# cancellation_summary와 selected_iso는 외부에서 정의된 값 사용 전제로 제거

def plot_cancellation_chart(df, iso):
    if iso == "Total":
        temp = df.groupby('year')[['account_count', 'volume_sum', 'profit_sum']].sum().reset_index()
    else:
        temp = df[df['iso'] == iso][['year', 'account_count', 'volume_sum', 'profit_sum']].copy()

    fig = px.bar(
        temp,
        x='year',
        y='account_count',
        color='year',
        text='account_count',
        color_discrete_map={2024: '#1f77b4', 2025: '#ff7f0e'},
        title="🛑 Cancellation Count (YOY)"
    )

    fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
    fig.update_layout(height=400, xaxis_tickangle=-15)
    st.plotly_chart(fig, use_container_width=True)

    table_df = temp.set_index('year')[['account_count', 'volume_sum', 'profit_sum']].copy()
    if 2024 in table_df.index and 2025 in table_df.index:
        yoy = ((table_df.loc[2025] - table_df.loc[2024]) / table_df.loc[2024].replace(0, pd.NA)) * 100
        table_df.loc['YOY'] = yoy.round(1).astype(str) + '%'

    table_df[['volume_sum', 'profit_sum']] = table_df[['volume_sum', 'profit_sum']].applymap(lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) else x)
    st.markdown("### 📊 Cancellation Data Table")
    st.dataframe(table_df, use_container_width=True)

# 대시보드에 출력 (기존 코드에서 cancellation_summary, selected_iso가 정의된 이후 위치해야 함)
# st.subheader("📉 Cancellation Overview")
# plot_cancellation_chart(cancellation_summary, selected_iso)
