import streamlit as st
import time

# ------------------ Hero Section ------------------
st.markdown(
    """
    <div style='background-color:#0a0a0a;padding:30px;border-radius:10px;text-align:center'>
        <h1 style='color:#00ffff;margin-bottom:5px;'>Round Robin CPU Scheduler Simulator</h1>
        <p style='color:#ccc;margin-top:0;'>Visualize processes moving through CPU using Round Robin scheduling. Adjust Time Quantum and watch step-by-step execution.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------ Sidebar Controls ------------------
st.sidebar.header("Simulation Controls")
time_quantum = st.sidebar.number_input("Time Quantum", min_value=1, value=3)
start_btn = st.sidebar.button("Start Simulation")
reset_btn = st.sidebar.button("Reset")

# ------------------ Process Definitions ------------------
processes = [
    {"id": "P1", "burst_time": 8, "arrival_time": 0, "color": "#e91e63"},
    {"id": "P2", "burst_time": 5, "arrival_time": 2, "color": "#9c27b0"},
    {"id": "P3", "burst_time": 12, "arrival_time": 4, "color": "#3f51b5"},
    {"id": "P4", "burst_time": 6, "arrival_time": 6, "color": "#009688"},
]

# ------------------ Initialize State ------------------
if "process_data" not in st.session_state or reset_btn:
    st.session_state.process_data = [
        {
            **p,
            "remaining_time": p["burst_time"],
            "waiting_time": 0,
            "has_arrived": False,
            "completion_time": 0
        }
        for p in processes
    ]
    st.session_state.ready_queue = []
    st.session_state.current_time = 0
    st.session_state.history_log = []  # Scrollable history log
    st.session_state.running = False

# ------------------ Layout ------------------
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    st.subheader("Processes")
    process_container = st.empty()

with col2:
    st.subheader("CPU")
    cpu_container = st.empty()
    st.subheader("Ready Queue")
    ready_queue_container = st.empty()
    st.subheader("History Log")
    history_container = st.empty()

with col3:
    st.subheader("Statistics")
    stats_container = st.empty()

# ------------------ Helper Functions ------------------
def render_processes():
    html = ""
    for p in st.session_state.process_data:
        html += f"<div style='color:{p['color']};margin-bottom:5px;'>"
        html += f"{p['id']} | BT: {p['remaining_time']} | AT: {p['arrival_time']} | WT: {p['waiting_time']}</div>"
    process_container.markdown(html, unsafe_allow_html=True)

def render_cpu(process=None):
    if process:
        cpu_container.markdown(
            f"<div style='padding:10px;background:{process['color']};color:white;border-radius:5px;text-align:center'>{process['id']}</div>",
            unsafe_allow_html=True,
        )
    else:
        cpu_container.markdown(
            "<div style='padding:10px;background:#111;color:white;border-radius:5px;text-align:center'>Idle</div>",
            unsafe_allow_html=True,
        )

def render_ready_queue():
    html = ""
    for p in st.session_state.ready_queue:
        html += f"<span style='display:inline-block;margin-right:5px;padding:5px;background:{p['color']};color:white;border-radius:5px'>{p['id']}</span>"
    ready_queue_container.markdown(html, unsafe_allow_html=True)

def render_history():
    html = "<div style='height:300px;overflow-y:scroll;border:1px solid #555;padding:5px;background:#111;'>"
    for entry in st.session_state.history_log:
        html += f"<div style='color:#e0e0e0;margin-bottom:5px;'>{entry}</div>"
    html += "</div>"
    history_container.markdown(html, unsafe_allow_html=True)

def render_stats():
    total_wt = sum(p['waiting_time'] for p in st.session_state.process_data)
    total_tat = sum((p['completion_time'] - p['arrival_time']) for p in st.session_state.process_data)
    n = len(st.session_state.process_data)
    avg_wt = total_wt / n
    avg_tat = total_tat / n
    html = f"""
    <div style='color:#00ffff'>
        <p>Total Waiting Time: {total_wt}</p>
        <p>Average Waiting Time: {avg_wt:.2f}</p>
        <p>Total Turnaround Time: {total_tat}</p>
        <p>Average Turnaround Time: {avg_tat:.2f}</p>
    </div>
    """
    stats_container.markdown(html, unsafe_allow_html=True)

# ------------------ Simulation ------------------
if start_btn and not st.session_state.running:
    st.session_state.running = True
    while any(p["remaining_time"] > 0 for p in st.session_state.process_data):
        # Check arrivals
        for p in st.session_state.process_data:
            if not p["has_arrived"] and p["arrival_time"] <= st.session_state.current_time:
                p["has_arrived"] = True
                st.session_state.ready_queue.append(p)
                st.session_state.history_log.append(f"[Time {st.session_state.current_time}] {p['id']} arrived in Ready Queue.")

        # Take next process
        if st.session_state.ready_queue:
            current_process = st.session_state.ready_queue.pop(0)
            st.session_state.history_log.append(f"[Time {st.session_state.current_time}] {current_process['id']} moved to CPU.")

            time_to_run = min(current_process["remaining_time"], time_quantum)
            for _ in range(time_to_run):
                current_process["remaining_time"] -= 1
                st.session_state.current_time += 1

                # Increment waiting time for others
                for p in st.session_state.ready_queue:
                    p["waiting_time"] += 1

                # Check arrivals during execution
                for p in st.session_state.process_data:
                    if not p["has_arrived"] and p["arrival_time"] <= st.session_state.current_time:
                        p["has_arrived"] = True
                        st.session_state.ready_queue.append(p)
                        st.session_state.history_log.append(f"[Time {st.session_state.current_time}] {p['id']} arrived in Ready Queue.")

                # Render
                render_processes()
                render_cpu(current_process)
                render_ready_queue()
                render_history()
                render_stats()
                time.sleep(0.5)

            # Post execution
            if current_process["remaining_time"] > 0:
                st.session_state.ready_queue.append(current_process)
                st.session_state.history_log.append(f"[Time {st.session_state.current_time}] {current_process['id']} returned to Ready Queue.")
            else:
                current_process['completion_time'] = st.session_state.current_time
                st.session_state.history_log.append(f"[Time {st.session_state.current_time}] {current_process['id']} finished execution.")

        else:
            # CPU idle
            st.session_state.current_time += 1
            render_cpu(None)
            render_processes()
            render_ready_queue()
            render_history()
            render_stats()
            time.sleep(0.5)

    st.session_state.running = False
    st.success("Simulation Complete!")
