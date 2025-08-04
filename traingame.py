import streamlit as st
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# --- Google Sheets Setup ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("TrainGameLeaderboard").sheet1

# Points mapping for runs
POINTS_MAP = {
    1: 0, 2: 1, 3: 3, 4: 5, 5: 7, 6: 9, 7: 11, 8: 15, 9: 20, 10: 25,
    11: 30, 12: 35, 13: 40, 14: 50, 15: 60, 16: 70, 17: 85, 18: 100, 19: 150, 20: 300
}

# Initialize session state variables
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
    st.session_state.game_over = False

if "player_name" not in st.session_state:
    st.session_state.player_name = ""

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

def get_next_number():
    if st.session_state.remaining_sample:
        st.session_state.current_number = st.session_state.remaining_sample.pop(0)
        st.session_state.output.append(st.session_state.current_number)
        st.session_state.awaiting_input = True
    else:
        st.session_state.game_over = True
        st.session_state.awaiting_input = False
        st.session_state.current_number = None
        # Calculate score info
        runs = calculate_runs()
        points = calculate_points(runs)
        # Use the player name from session state or default to Anonymous User
        player = st.session_state.player_name.strip() or "Anonymous User"
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        best_run = max(runs) if runs else 0
        sheet.append_row([player, points, best_run, date_str])

# --- Title ---
st.markdown("<h1>🚂 Math Train Game 🚂</h1>", unsafe_allow_html=True)

# --- Player Name Input  ---
player_name = st.text_input(
    label="",
    placeholder="Optional: Enter Name for Leaderboard",
    key="player_name",
    label_visibility="collapsed"
)

# --- Buttons ---
col1, col2, col3, col4 = st.columns([2, 2, 1, 4])
with col1:
    if st.button("New Number", disabled=st.session_state.awaiting_input or not st.session_state.remaining_sample or st.session_state.game_over):
        get_next_number()
with col2:
    if st.button("New Game"):
        st.session_state.sampled_values = random.sample(st.session_state.original_pool, 20)
        st.session_state.remaining_sample = st.session_state.sampled_values.copy()
        st.session_state.output = []
        st.session_state.current_number = None
        st.session_state.locked_boxes = set()
        st.session_state.awaiting_input = False
        st.session_state.box_counter = 1
        st.session_state.game_over = False
        for i in range(1, 21):
            st.session_state[f"box_{i}"] = ""

with col4:
   st.markdown(
        """
        <a href="https://docs.google.com/spreadsheets/d/1hugxTaenv-YjBbHIvXLWdxaXifIuiNp71KN75fmw0qw/edit?usp=sharing" target="_blank" style="font-size:20px; text-decoration:none;">
            📊 View Leaderboard
        </a>
        """,
        unsafe_allow_html=True
    )

# --- Game finished message ---
if st.session_state.game_over:
    runs = calculate_runs()
    points = calculate_points(runs)
    runs_str = ", ".join(str(r) for r in runs)
    st.markdown(
        f"<div style='font-size:22px; color:green; margin-top: 10px; margin-bottom: 10px;'>✅ Game Finished. Your Runs: {runs_str}. Your Score: {points}. Click 'Reset' to play again.</div>",
        unsafe_allow_html=True,
    )

# --- Drawn numbers ---
st.write("### Numbers shown so far:")
st.write(", ".join(str(num) for num in st.session_state.output))

# --- Input Grid ---
with st.container():
    st.divider()
    st.subheader("Enter Your Numbers In The Train")

    input_positions = {
        (4, 0): 1, (3, 0): 2, (2, 0): 3, (1, 0): 4, (0, 0): 5,
        (0, 1): 6, (0, 2): 7, (0, 3): 8, (0, 4): 9, (0, 5): 10,
        (0, 6): 11, (0, 7): 12, (0, 8): 13, (0, 9): 14, (0, 10): 15,
        (0, 11): 16, (1, 11): 17, (2, 11): 18, (3, 11): 19, (4, 11): 20,
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
                    label="Input for number",
                    key=key,
                    value=value,
                    disabled=disabled,
                    label_visibility="collapsed",
                    on_change=make_callback(box_num),
                )
            else:
                cols[col].markdown(" ")

  

# --- Live scoring ---
runs = calculate_runs()
points = calculate_points(runs)
st.write("### Current runs of non-decreasing numbers:")
st.write(runs)
st.write(f"### Current points: {points}")
