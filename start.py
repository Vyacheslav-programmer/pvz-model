# -*- coding: utf-8 -*-
import streamlit as st

st.set_page_config(
    page_title="Модель ПВЗ",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📦 Имитационная модель работы пункта выдачи заказов")
st.write(
    "Модель описывает процесс обслуживания клиентов в ПВЗ с учётом "
    "технических перерывов (приём/разгрузка товара)."
)

st.sidebar.header("Навигация")
st.sidebar.page_link("pages/Main_model.py", label="Базовая модель")
st.sidebar.page_link("pages/Experiment_1.py", label="Эксперимент 1: число окон")
st.sidebar.page_link("pages/Experiment_2.py", label="Эксперимент 2: интенсивность потока")

st.divider()
st.subheader("Структурная схема модели")

dot_string = """
digraph PVZ {
    rankdir=TB;
    node [shape=rectangle, style=filled, fillcolor=lightblue, fontname="Arial"];
    A [label="Входной поток\\nклиентов"];
    B [label="Очередь к окнам\\nвыдачи"];
    C [label="Окна выдачи\\n(N каналов)"];
    D [label="Блок\\nтехнического\\nперерыва", fillcolor=lightyellow];
    E [label="Выход\\nклиентов"];
    A -> B; B -> C;
    D -> C [style=dashed, label="перерыв"];
    C -> E;
}
"""
st.graphviz_chart(dot_string)