# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import pvz_model as mdl

st.set_page_config(page_title="Эксперимент 2 — интенсивность", page_icon="📦", layout="wide")

st.title("📊 Эксперимент 2: влияние интенсивности потока")

with st.sidebar:
    st.header("Навигация")
    st.page_link("start.py", label="[ Стартовая страница ]")
    st.page_link("pages/Main_model.py", label="[ Базовая модель ]")
    st.header("Параметры эксперимента")
    min_arr = st.slider("Мин. интервал (мин)", 1.0, 10.0, 2.0, 0.5)
    max_arr = st.slider("Макс. интервал (мин)", 1.0, 10.0, 6.0, 0.5)
    step_arr = st.slider("Шаг изменения (мин)", 0.5, 3.0, 1.0, 0.5)
    replications = st.slider("Число прогонов", 1, 20, 5)
    num_windows = st.slider("Число окон", 1, 5, 2)
    sim_time = st.slider("Время моделирования (мин)", 60, 600, 480, 30)
    run_btn = st.button("▶ Запустить эксперимент")

if run_btn and max_arr >= min_arr:
    levels = []
    a = min_arr
    while a <= max_arr:
        levels.append(a)
        a += step_arr
    
    results = []
    progress = st.progress(0)
    total = len(levels) * replications
    count = 0
    
    for arr_mean in levels:
        for rep in range(replications):
            params = {
                "arrival_mean": arr_mean,
                "service_mean": 4.0,
                "service_std": 1.0,
                "num_windows": num_windows,
                "break_duration": 15,
                "break_interval": 120,
                "sim_time": sim_time,
                "seed": 42 + rep + int(arr_mean * 100),
            }
            events, _ = mdl.model_env(params)
            summary = mdl.summary_from_events(events)
            summary["arrival_mean"] = arr_mean
            results.append(summary)
            count += 1
            progress.progress(count / total)
    
    df = pd.DataFrame(results)
    st.subheader("Сырые результаты")
    st.dataframe(df, use_container_width=True)
    
    df_group = df.groupby("arrival_mean").agg({
        "avg_wait": "mean",
        "avg_system_time": "mean",
        "p_otk": "mean"
    }).reset_index().sort_values("arrival_mean")
    
    st.subheader("Агрегированные результаты")
    st.dataframe(df_group, use_container_width=True)
    
    st.subheader("Среднее время ожидания в зависимости от интервала между клиентами")
    st.line_chart(df_group.set_index("arrival_mean")["avg_wait"], use_container_width=True)