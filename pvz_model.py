# -*- coding: utf-8 -*-
"""
pvz_model.py — Ядро имитационной модели ПВЗ с техническими перерывами.
"""

import random as rd
import simpy

# --- Параметры по умолчанию ---
ARRIVAL_MEAN = 3.0      # средний интервал между клиентами (мин)
SERVICE_MEAN = 4.0      # среднее время обслуживания (мин)
SERVICE_STD = 1.0       # СКО времени обслуживания
NUM_WINDOWS = 2         # количество окон выдачи
SIM_TIME = 480          # время моделирования (8 часов)
BREAK_DURATION = 15     # длительность перерыва (мин)
BREAK_INTERVAL = 120    # интервал между перерывами (мин)
MAX_QUEUE = 20          # максимальная длина очереди (отказ при превышении)

class Globals:
    """Хранилище статистики для одного прогона."""
    event_log = []
    queue_log = []

def client(env, pid, windows, break_event):
    """Процесс клиента: приход → очередь → обслуживание → выход."""
    arrival_time = env.now
    
    # Проверка на переполнение очереди
    if len(windows.queue) >= MAX_QUEUE:
        Globals.event_log.append({
            "patient": pid,
            "t_arrival": arrival_time,
            "t_start": None,
            "t_end": None,
            "wait": None,
            "system_time": None,
            "status": "отказ"
        })
        return
    
    with windows.request() as req:
        yield req
        start_time = env.now
        wait_time = start_time - arrival_time
        
        service_time = max(0.1, rd.gauss(SERVICE_MEAN, SERVICE_STD))
        yield env.timeout(service_time)
        
        end_time = env.now
        Globals.event_log.append({
            "patient": pid,
            "t_arrival": arrival_time,
            "t_start": start_time,
            "t_end": end_time,
            "wait": wait_time,
            "system_time": end_time - arrival_time,
            "status": "обслужен"
        })

def client_arrivals(env, windows, break_event):
    """Генератор потока клиентов."""
    pid = 0
    while True:
        interarrival = rd.expovariate(1.0 / ARRIVAL_MEAN)
        yield env.timeout(interarrival)
        pid += 1
        env.process(client(env, pid, windows, break_event))

def technical_break(env, break_event, windows):
    """Генератор технических перерывов."""
    while True:
        yield env.timeout(BREAK_INTERVAL)
        # Начало перерыва — блокируем окна
        break_event.succeed()
        break_event = env.event()
        yield env.timeout(BREAK_DURATION)

def monitor_queue(env, windows, sim_time):
    """Мониторинг длины очереди каждую минуту."""
    while env.now < sim_time:
        Globals.queue_log.append(len(windows.queue))
        yield env.timeout(1.0)

def model_env(config=None):
    """Запуск модели с заданными параметрами."""
    global ARRIVAL_MEAN, SERVICE_MEAN, SERVICE_STD, NUM_WINDOWS, SIM_TIME, BREAK_DURATION, BREAK_INTERVAL, MAX_QUEUE
    
    if config:
        ARRIVAL_MEAN = float(config.get("arrival_mean", ARRIVAL_MEAN))
        SERVICE_MEAN = float(config.get("service_mean", SERVICE_MEAN))
        SERVICE_STD = float(config.get("service_std", SERVICE_STD))
        NUM_WINDOWS = int(config.get("num_windows", NUM_WINDOWS))
        SIM_TIME = float(config.get("sim_time", SIM_TIME))
        BREAK_DURATION = float(config.get("break_duration", BREAK_DURATION))
        BREAK_INTERVAL = float(config.get("break_interval", BREAK_INTERVAL))
        MAX_QUEUE = int(config.get("max_queue", MAX_QUEUE))
        seed = config.get("seed", None)
        if seed is not None:
            rd.seed(seed)
    
    Globals.event_log = []
    Globals.queue_log = []
    
    env = simpy.Environment()
    windows = simpy.Resource(env, capacity=NUM_WINDOWS)
    break_event = env.event()
    
    env.process(client_arrivals(env, windows, break_event))
    env.process(technical_break(env, break_event, windows))
    env.process(monitor_queue(env, windows, SIM_TIME))
    
    env.run(until=SIM_TIME)
    
    return Globals.event_log, {"queue": Globals.queue_log}

def summary_from_events(event_log):
    """Подсчёт средних метрик."""
    served = [e for e in event_log if e["status"] == "обслужен"]
    rejected = [e for e in event_log if e["status"] == "отказ"]
    
    n_serv = len(served)
    n_otk = len(rejected)
    
    avg_wait = sum(e["wait"] for e in served) / n_serv if n_serv > 0 else 0
    avg_system = sum(e["system_time"] for e in served) / n_serv if n_serv > 0 else 0
    
    return {
        "n_served": n_serv,
        "n_rejected": n_otk,
        "avg_wait": avg_wait,
        "avg_system_time": avg_system,
        "p_otk": n_otk / (n_serv + n_otk) if (n_serv + n_otk) > 0 else 0
    }

if __name__ == "__main__":
    events, queues = model_env()
    print(f"Обслужено: {len([e for e in events if e['status']=='обслужен'])}")
    print(f"Отказов: {len([e for e in events if e['status']=='отказ'])}")