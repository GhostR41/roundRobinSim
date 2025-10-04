import streamlit as st
import time

st.set_page_config(layout="wide")
st.title("Animated Round Robin Simulator")

# ---- Sidebar Controls ----
st.sidebar.header("Simulation Controls")
time_quantum = st.sidebar.number_input("Time Quantum", min_value=1, value=3)
start_btn = st.sidebar.button("Start Simulation")
reset_btn = st.sidebar.button("Reset")

# ---- Define Processes ----
processes = [
    {"id": "P1", "burst_time": 8, "arrival_time": 0, "color": "#e91e63"},
    {"id": "P2", "burst_time": 5, "arrival_time": 2, "color": "#9c27b0"},
    {"id": "P3", "burst_time": 12, "arrival_time": 4, "color": "#3f51b5"},
    {"id": "P4", "burst_time": 6, "arrival_time": 6, "color": "#009688"},
]

# ---- Initialize State ----
if "process_data" not in st.session_state or reset_btn:
    st.session_state.process_data = [
        {
            **p,
            "remaining_time": p["burst_time"],
            "waiting_time": 0,
            "has_arrived": False,
        }
        for p in processes
    ]
    st.session_state.ready_queue = []
    st.session_state.current_time = 0
    st.session_state.history_log = []
    st.session_state.running = False

# ---- Layout Placeholders ----
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("Processes")
    process_container = st.empty()

with col2:
    st.subheader("Ready Queue")
    queue_container = st.empty()
    st.subheader("CPU")
    cpu_container = st.empty()

with col3:
    st.subheader("History Log")
    log_container = st.empty()
    st.subheader("Final Waiting Times")
    final_container = st.empty()

# ---- Helper Functions ----
def render_processes():
    text = ""
    for p in st.session_state.process_data:
        text += f"<div style='color:{p['color']};'>"
        text += f"{p['id']} | BT: {p['remaining_time']} | AT: {p['arrival_time']} | WT: {p['waiting_time']}</div>"
    process_container.markdown(text, unsafe_allow_html=True)

def render_ready_queue():
    queue_text = ""
    for p in st.session_state.ready_queue:
        queue_text += f"<div style='display:inline-block;margin:5px;padding:5px;background:{p['color']};color:white;border-radius:5px'>{p['id']}</div>"
    queue_container.markdown(queue_text, unsafe_allow_html=True)

def render_cpu(process=None):
    if process:
        cpu_container.markdown(
            f"<div style='padding:10px;background:{process['color']};color:white;border-radius:5px'>{process['id']}</div>",
            unsafe_allow_html=True,
        )
    else:
        cpu_container.markdown(
            "<div style='padding:10px;background:#111;color:white;border-radius:5px'>Idle</div>",
            unsafe_allow_html=True,
        )

def render_log():
    log_text = ""
    for entry in st.session_state.history_log:
        log_text += f"<div>{entry}</div>"
    log_container.markdown(log_text, unsafe_allow_html=True)

def render_final_waiting_times():
    text = ""
    for p in st.session_state.process_data:
        text += f"<div>{p['id']}: {p['waiting_time']} units</div>"
    final_container.markdown(text, unsafe_allow_html=True)

# ---- Animated Simulation ----
if start_btn and not st.session_state.running:
    st.session_state.running = True
    while any(p["remaining_time"] > 0 for p in st.session_state.process_data):
        # Check arrivals
        for p in st.session_state.process_data:
            if not p["has_arrived"] and p["arrival_time"] <= st.session_state.current_time:
                p["has_arrived"] = True
                st.session_state.ready_queue.append(p)
                st.session_state.history_log.append(
                    f"[Time {st.session_state.current_time}] {p['id']} arrived in Ready Queue."
                )

        # CPU Execution
        if st.session_state.ready_queue:
            current_process = st.session_state.ready_queue.pop(0)
            st.session_state.history_log.append(
                f"[Time {st.session_state.current_time}] {current_process['id']} moved to CPU."
            )

            # Animate CPU execution step by step
            render_processes()
            render_ready_queue()
            render_cpu(current_process)
            render_log()
            render_final_waiting_times()
            time.sleep(1)

            time_to_run = min(current_process["remaining_time"], time_quantum)
            for _ in range(time_to_run):
                current_process["remaining_time"] -= 1
                st.session_state.current_time += 1
                # Update waiting time for others
                for p in st.session_state.ready_queue:
                    p["waiting_time"] += 1

                # Check arrivals during execution
                for p in st.session_state.process_data:
                    if not p["has_arrived"] and p["arrival_time"] <= st.session_state.current_time:
                        p["has_arrived"] = True
                        st.session_state.ready_queue.append(p)
                        st.session_state.history_log.append(
                            f"[Time {st.session_state.current_time}] {p['id']} arrived in Ready Queue."
                        )

                render_processes()
                render_ready_queue()
                render_cpu(current_process)
                render_log()
                render_final_waiting_times()
                time.sleep(0.5)

            # Post execution
            if current_process["remaining_time"] > 0:
                st.session_state.ready_queue.append(current_process)
                st.session_state.history_log.append(
                    f"[Time {st.session_state.current_time}] {current_process['id']} returned to Ready Queue."
                )
            else:
                st.session_state.history_log.append(
                    f"[Time {st.session_state.current_time}] {current_process['id']} finished execution."
                )
        else:
            # CPU idle
            st.session_state.current_time += 1
            render_cpu(None)
            time.sleep(0.5)
            render_processes()
            render_ready_queue()
            render_log()
            render_final_waiting_times()

    st.session_state.running = False
    render_final_waiting_times()
