# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pvz_model as mdl

st.set_page_config(page_title="Модель ПВЗ — базовая", page_icon="📦", layout="wide")

st.title("📦 Базовая модель работы ПВЗ")

with st.sidebar:
    st.header("Параметры прогона")
    st.page_link("start.py", label="[ Стартовая страница ]")
    
    with st.form(key="input_form"):
        arrival_mean = st.slider("Средний интервал между клиентами (мин)", 1.0, 15.0, 3.0, 0.5)
        service_mean = st.slider("Среднее время обслуживания (мин)", 1.0, 15.0, 4.0, 0.5)
        service_std = st.slider("СКО времени обслуживания (мин)", 0.1, 5.0, 1.0, 0.1)
        num_windows = st.slider("Количество окон выдачи", 1, 5, 2)
        break_duration = st.slider("Длительность перерыва (мин)", 5, 30, 15, 1)
        break_interval = st.slider("Интервал между перерывами (мин)", 60, 240, 120, 10)
        sim_time = st.slider("Время моделирования (мин)", 60, 600, 480, 30)
        seed = st.number_input("Seed ГСЧ", 0, 10000, 42)
        run_btn = st.form_submit_button("▶ Запуск модели")

params = {
    "arrival_mean": arrival_mean,
    "service_mean": service_mean,
    "service_std": service_std,
    "num_windows": num_windows,
    "break_duration": break_duration,
    "break_interval": break_interval,
    "sim_time": sim_time,
    "seed": int(seed),
}

if run_btn:
    with st.spinner("Выполняется моделирование..."):
        events, queues = mdl.model_env(params)
        df_events = pd.DataFrame(events)
        df_queues = pd.DataFrame(queues)
        summary = mdl.summary_from_events(events)
    
    st.success("Моделирование завершено.")
    
    st.subheader("📊 Итоговые показатели")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Обслужено", summary["n_served"])
    col2.metric("Отказов", summary["n_rejected"])
    col3.metric("Среднее ожидание (мин)", f"{summary['avg_wait']:.2f}")
    col4.metric("Вероятность отказа", f"{summary['p_otk']*100:.1f}%")
    
    st.subheader("📈 График длины очереди")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df_queues.index, df_queues["queue"])
    ax.set_xlabel("Время (мин)")
    ax.set_ylabel("Длина очереди")
    ax.grid(True)
    st.pyplot(fig)
    
    st.subheader("📋 Журнал клиентов")
    st.dataframe(df_events.head(20), use_container_width=True)