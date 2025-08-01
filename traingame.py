import streamlit as st
import random

# Points mapping for runs (run length -> points)
POINTS_MAP = {
    1: 0, 2: 1, 3: 3, 4: 5, 5: 7, 6: 9, 7: 11, 8: 15, 9: 20, 10: 25,
    11: 30, 12: 35, 13: 40, 14: 50, 15: 60, 16: 70, 17: 85, 18: 100, 19: 150, 20: 300
}

# Initialize session state
if 'original_pool' not in st.session_state:
    st.session_state.original_pool = [
        1,2,3,4,5,6,7,8,9,10,
        11,11,12,12,13,13,14,14,15,15,
        16,16,17,17,18,18,19,19,
        20,21,22,23,24,25,26,27,28,29,30
    ]
    st.session_state.sampled_values = random.sample(st.session_state.original_pool, 20)
    st.session_state.remaining_sample = st.session_state.sampled_values.copy()
    st.session_state.output = []
    st.session_state.current_number = None
    st.session_state.locked_boxes = set()
    st.session_state.awaiting_input = False
    st.session_state.box_counter = 1

st.title("🎲 Math Train Game")

# --- Run and Point Calculation ---
def calculate_runs():
    entered_numbers = []
    for i in range(1, 21):
        val = st.session_state.get(f"box_{i}", "")
        try:
            entered_numbers.append(int(val))
        except:
            entered_numbers.append(None)

    runs = []
    if entered_numbers:
        run_length = 1
        for i in range(1, len(entered_numbers)):
            prev = entered_numbers[i-1]
            curr = entered_numbers[i]
            if prev is None or curr is None:
                runs.append(run_length)
                run_length = 1
            elif curr >= prev:
                run_length += 1
            else:
                runs.append(run_length)
                run_length = 1
        runs.append(run_length)
    return runs

def calculate_points(runs):
    return sum(POINTS_MAP.get(r, 0) for r in runs)

# --- Number Drawing Logic ---
def get_next_number():
    if st.session_state.remaining_sample:
        st.session_state.current_number = st.session_state.remaining_sample.pop(0)
        st.session_state.output.append(st.session_state.current_number)
        st.session_state.awaiting_input = True
    else:
        runs = calculate_runs()
        points = calculate_points(runs)
        runs_str = ", ".join(str(r) for r in runs)
        st.markdown(
            f"<div style='font-size:22px; color:green;'>✅ All 20 numbers shown. Runs: {runs_str}. Points: {points}. Click 'Reset' to start again.</div>",
            unsafe_allow_html=True
        )
        st.session_state.current_number = None
        st.session_state.awaiting_input = False

# --- Top Controls ---
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Next Number", disabled=st.session_state.awaiting_input or not st.session_state.remaining_sample):
        get_next_number()

with col2:
    if st.button("Reset"):
        st.session_state.sampled_values = random.sample(st.session_state.original_pool, 20)
        st.session_state.remaining_sample = st.session_state.sampled_values.copy()
        st.session_state.output = []
        st.session_state.current_number = None
        st.session_state.locked_boxes = set()
        st.session_state.awaiting_input = False
        st.session_state.box_counter = 1
        for i in range(1, 21):
            st.session_state[f"box_{i}"] = ""
        get_next_number()

# --- Display Drawn Numbers ---
st.write("### Numbers shown so far:")
st.write(", ".join(str(num) for num in st.session_state.output))

# --- Layout Definitions ---
st.divider()
st.subheader("Enter Your Numbers")

input_positions = {
    (4, 0): 1,
    (3, 0): 2,
    (2, 0): 3,
    (1, 0): 4,
    (0, 0): 5,
    (0, 1): 6,
    (0, 2): 7,
    (0, 3): 8,
    (0, 4): 9,
    (0, 5): 10,
    (0, 6): 11,
    (0, 7): 12,
    (0, 8): 13,
    (0, 9): 14,
    (0, 10): 15,
    (0, 11): 16,
    (1, 11): 17,
    (2, 11): 18,
    (3, 11): 19,
    (4, 11): 20,
}

def make_callback(box_num):
    def callback():
        key = f"box_{box_num}"
        val = st.session_state.get(key, "")
        if st.session_state.current_number is not None:
            if val == str(st.session_state.current_number):
                st.session_state.locked_boxes.add(box_num)
                st.session_state.awaiting_input = False
                st.session_state.current_number = None
                st.session_state.box_counter += 1
                get_next_number()
    return callback

for row in range(5):
    cols = st.columns(12)
    for col in range(12):
        box_num = input_positions.get((row, col))
        if box_num:
            key = f"box_{box_num}"
            value = st.session_state.get(key, "")
            disabled = box_num in st.session_state.locked_boxes

            cols[col].text_input(
                label="",
                key=key,
                value=value,
                disabled=disabled,
                label_visibility="collapsed",
                on_change=make_callback(box_num),
            )
        else:
            cols[col].markdown(" ")

# --- Styling ---
st.markdown("""
    <style>
        div[data-testid="stTextInput"] input {
            width: 50px !important;
            height: 50px !important;
            font-size: 25px !important;
            text-align: center !important;
            padding: 0 !important;
            margin: 5px auto !important;
            box-sizing: border-box !important;
        }
        div[data-testid="stTextInput"] {
            max-width: 50px !important;
            min-width: 50px !important;
            max-height: 50px !important;
            min-height: 50px !important;
            margin: 5px auto !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- Live Run/Point Display ---
runs = calculate_runs()
points = calculate_points(runs)
st.write("### Current runs of non-decreasing numbers:")
st.write(runs)
st.write(f"### Current points: {points}")
