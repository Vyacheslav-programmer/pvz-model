# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import pvz_model as mdl

st.set_page_config(page_title="Эксперимент 1 — число окон", page_icon="📦", layout="wide")

st.title("📊 Эксперимент 1: влияние количества окон")

with st.sidebar:
    st.header("Навигация")
    st.page_link("start.py", label="[ Стартовая страница ]")
    st.page_link("pages/Main_model.py", label="[ Базовая модель ]")
    st.header("Параметры эксперимента")
    min_win = st.slider("Мин. число окон", 1, 5, 1)
    max_win = st.slider("Макс. число окон", 1, 5, 4)
    replications = st.slider("Число прогонов", 1, 20, 5)
    arrival_mean = st.slider("Средний интервал (мин)", 1.0, 15.0, 3.0, 0.5)
    sim_time = st.slider("Время моделирования (мин)", 60, 600, 480, 30)
    run_btn = st.button("▶ Запустить эксперимент")

if run_btn and max_win >= min_win:
    results = []
    progress = st.progress(0)
    total = (max_win - min_win + 1) * replications
    count = 0
    
    for n_win in range(min_win, max_win + 1):
        for rep in range(replications):
            params = {
                "arrival_mean": arrival_mean,
                "service_mean": 4.0,
                "service_std": 1.0,
                "num_windows": n_win,
                "break_duration": 15,
                "break_interval": 120,
                "sim_time": sim_time,
                "seed": 42 + rep + 1000 * n_win,
            }
            events, _ = mdl.model_env(params)
            summary = mdl.summary_from_events(events)
            summary["num_windows"] = n_win
            results.append(summary)
            count += 1
            progress.progress(count / total)
    
    df = pd.DataFrame(results)
    st.subheader("Сырые результаты")
    st.dataframe(df, use_container_width=True)
    
    df_group = df.groupby("num_windows").agg({
        "avg_wait": "mean",
        "avg_system_time": "mean",
        "p_otk": "mean"
    }).reset_index()
    
    st.subheader("Агрегированные результаты")
    st.dataframe(df_group, use_container_width=True)
    
    st.subheader("Среднее время ожидания в зависимости от числа окон")
    st.bar_chart(df_group.set_index("num_windows")["avg_wait"], use_container_width=True)