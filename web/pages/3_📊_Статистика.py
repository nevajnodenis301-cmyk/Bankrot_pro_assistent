import streamlit as st
st.set_page_config(page_title="Статистика", page_icon="📊", layout="wide")

import httpx
import os
import pandas as pd
import plotly.express as px

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.title("📊 Статистика")


@st.cache_data(ttl=60)
def get_cases():
    """Fetch all cases from API"""
    try:
        response = httpx.get(f"{API_URL}/api/cases")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {str(e)}")
        return []


# Refresh button
if st.button("🔄 Обновить"):
    st.cache_data.clear()
    st.rerun()

cases = get_cases()

if not cases:
    st.info("Нет данных для отображения статистики")
else:
    # Convert to DataFrame for analysis
    df = pd.DataFrame(cases)

    # General stats
    st.subheader("📈 Общая статистика")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Всего дел", len(df))

    with col2:
        total_debt = df["total_debt"].fillna(0).sum()
        st.metric("Общий долг", f"{total_debt:,.0f} ₽")

    with col3:
        avg_debt = df["total_debt"].fillna(0).mean()
        st.metric("Средний долг", f"{avg_debt:,.0f} ₽")

    with col4:
        total_creditors = df["creditors_count"].fillna(0).sum()
        st.metric("Всего кредиторов", int(total_creditors))

    st.divider()

    # Status distribution
    st.subheader("📊 Распределение по статусам")

    status_counts = df["status"].value_counts()
    status_labels = {
        "new": "Новые",
        "in_progress": "В работе",
        "court": "В суде",
        "completed": "Завершенные",
    }
    status_counts.index = status_counts.index.map(lambda x: status_labels.get(x, x))

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Количество дел по статусам",
            hole=0.3,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.dataframe(
            status_counts.reset_index().rename(columns={"index": "Статус", "status": "Количество"}),
            hide_index=True,
            use_container_width=True,
        )

    st.divider()

    # Debt distribution
    st.subheader("💰 Распределение долгов")

    debt_data = df[df["total_debt"] > 0]["total_debt"]

    if len(debt_data) > 0:
        col1, col2 = st.columns(2)

        with col1:
            fig_hist = px.histogram(
                debt_data, nbins=20, title="Распределение размера долгов", labels={"value": "Сумма долга (₽)"}
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            st.write("**Статистика по долгам:**")
            st.write(f"- Минимум: {debt_data.min():,.0f} ₽")
            st.write(f"- Максимум: {debt_data.max():,.0f} ₽")
            st.write(f"- Медиана: {debt_data.median():,.0f} ₽")
            st.write(f"- Среднее: {debt_data.mean():,.0f} ₽")
    else:
        st.info("Нет данных о долгах для анализа")

    st.divider()

    # Timeline
    st.subheader("📅 Динамика создания дел")

    if "created_at" in df.columns:
        df["created_date"] = pd.to_datetime(df["created_at"]).dt.date
        timeline = df.groupby("created_date").size().reset_index(name="count")

        fig_line = px.line(
            timeline,
            x="created_date",
            y="count",
            title="Количество созданных дел по дням",
            labels={"created_date": "Дата", "count": "Количество дел"},
        )
        st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # Recent cases
    st.subheader("🕒 Последние созданные дела")

    recent_cases = df.nlargest(5, "created_at")[["case_number", "full_name", "status", "total_debt", "created_at"]]
    recent_cases["total_debt"] = recent_cases["total_debt"].fillna(0).apply(lambda x: f"{x:,.0f} ₽")
    recent_cases["created_at"] = pd.to_datetime(recent_cases["created_at"]).dt.strftime("%d.%m.%Y %H:%M")

    st.dataframe(
        recent_cases.rename(
            columns={
                "case_number": "Номер дела",
                "full_name": "ФИО",
                "status": "Статус",
                "total_debt": "Долг",
                "created_at": "Создано",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )
