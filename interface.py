import streamlit as st
import pandas as pd
from datetime import date
import subprocess  # For external process call
import matplotlib.pyplot as plt

def order_combined_season(season_df):
    """
    Convert 'date' to datetime, recalc game_number for matches on the same day between the same teams,
    then sort by date (ascending) and game_number (ascending),
    and finally reformat the 'date' column as MM/DD/YYYY.
    """
    season_df['date'] = pd.to_datetime(season_df['date'], errors='coerce')
    season_df["match_key"] = season_df.apply(
        lambda row: f"{row['date'].strftime('%m/%d/%Y')}_{'_'.join(sorted([row['team'], row['opponent']]))}",
        axis=1
    )
    season_df["game_number"] = season_df.groupby("match_key").cumcount() + 1
    season_df.drop(columns=["match_key"], inplace=True)
    season_df = season_df.sort_values(['date', 'game_number']).reset_index(drop=True)
    season_df["date"] = season_df["date"].dt.strftime("%m/%d/%Y")
    return season_df

def order_simulated_matches(matches, ascending=True):
    """
    Order a list of simulated match dictionaries by date.
    Recalculate game_number for matches on the same day between the same teams,
    then return the ordered list of dictionaries.
    """
    if not matches:
        return matches
    df = pd.DataFrame(matches)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.sort_values('date', ascending=ascending).reset_index(drop=True)
    df["match_key"] = df.apply(
        lambda row: f"{row['date'].strftime('%m/%d/%Y')}_{'_'.join(sorted([row['team'] if pd.notnull(row['team']) else '', row['opponent'] if pd.notnull(row['opponent']) else '']))}",
        axis=1
    )
    df["game_number"] = df.groupby("match_key").cumcount() + 1
    df.drop(columns=["match_key"], inplace=True)
    df["date"] = df["date"].dt.strftime("%m/%d/%Y")
    return df.to_dict("records")

# Initialize session state variables.
if "reference_season_df" not in st.session_state:
    st.session_state.reference_season_df = None
if "simulated_matches" not in st.session_state:
    st.session_state.simulated_matches = []
if "simulated_mode" not in st.session_state:
    st.session_state.simulated_mode = None
if "mode_locked" not in st.session_state:
    st.session_state.mode_locked = False

st.title("Simulated Season Editor")

# ---------- MODE SELECTION ----------
st.header("Select Match Entry Mode")
mode_options = [
    "Full Match Entry (Date, Teams, and Result)",
    "Match Entry Without Result (Date and Teams Only)",
    "Date-Only Entry (Auto-generate schedule)"
]
mode_container = st.container()
if not st.session_state.mode_locked:
    with mode_container:
        selected_mode = st.radio("Select Match Entry Mode", mode_options)
        if st.button("Confirm Mode Selection"):
            st.session_state.simulated_mode = selected_mode
            st.session_state.mode_locked = True
            st.success(f"Mode locked as: {selected_mode}")
            mode_container.empty()
else:
    st.info(f"Current Mode: {st.session_state.simulated_mode}. Refresh to change.")

st.write("You are now operating in:", st.session_state.simulated_mode)

# ---------- UPLOAD REFERENCE SEASON CSV ----------
st.header("Upload Reference Season CSV")
with st.expander("What is the Reference Season?"):
    st.write("The Reference Season is your original season schedule template.")
uploaded_file = st.file_uploader("Upload the Reference Season CSV", type="csv")
if uploaded_file is not None:
    try:
        st.session_state.reference_season_df = pd.read_csv(uploaded_file)
        st.success("Reference Season CSV loaded successfully!")
        st.dataframe(st.session_state.reference_season_df.head())
    except Exception as e:
        st.error(f"Failed to read CSV file: {e}")

# ---------- NEW: Simulation Inputs ----------
if st.session_state.simulated_mode == "Match Entry Without Result (Date and Teams Only)":
    elo_num_simulations = st.number_input(
        "Enter number of ELO simulations", min_value=1, value=30, step=1
    )
    st.write(f"Number of ELO simulations: {elo_num_simulations}")

elif st.session_state.simulated_mode == "Date-Only Entry (Auto-generate schedule)":
    schedule_num_simulations = st.number_input(
        "Enter number of schedule simulations", min_value=1, value=10, step=1
    )
    st.write(f"Number of schedule simulations: {schedule_num_simulations}")

    elo_num_simulations = st.number_input(
        "Enter number of ELO simulations", min_value=1, value=30, step=1
    )
    st.write(f"Number of ELO simulations: {elo_num_simulations}")
# ---------- END NEW ----------

# ---------- MAIN WORKFLOW ----------
if st.session_state.reference_season_df is not None:
    df = st.session_state.reference_season_df

    # Select Team
    st.header("Select a Team to Simulate")
    teams_list = sorted(set(df["team"]) | set(df["opponent"]))
    selected_team = st.selectbox("Select the team to simulate", teams_list)
    if selected_team:
        st.write(f"You selected: {selected_team}")
        filtered_season = df[~((df["team"] == selected_team) | (df["opponent"] == selected_team))]
        st.subheader("Reference Season (After Removing Matches)")
        st.dataframe(filtered_season)
        st.session_state.filtered_season = filtered_season

        # Add Simulated Matches
        st.header("Add Simulated Matches")
        st.write(f"Mode: {st.session_state.simulated_mode}")
        with st.form("simform"):
            sim_date = st.date_input("Select match date", value=date.today())
            if st.session_state.simulated_mode in (
                "Full Match Entry (Date, Teams, and Result)",
                "Match Entry Without Result (Date and Teams Only)"
            ):
                all_teams = sorted(set(df["team"]) | set(df["opponent"]))
                opponent = st.selectbox("Opponent", [t for t in all_teams if t != selected_team])
                home_or_away = st.selectbox("Home/Away (Optional)", ["Not Specified", "Home", "Away"])
            else:
                opponent = ""
                home_or_away = ""
            if st.session_state.simulated_mode == "Full Match Entry (Date, Teams, and Result)":
                result_input = st.selectbox("Result", ["W", "L"])
                expanded = "W 1-0" if result_input == "W" else "L 0-1"
            else:
                result_input = ""
                expanded = ""
            submit_sim = st.form_submit_button("Add")
            if submit_sim:
                # NEW: Set default game_number and scores per mode
                if st.session_state.simulated_mode == "Full Match Entry (Date, Teams, and Result)":
                    home_score = 1 if result_input == "W" else 0
                    away_score = 1 if result_input == "L" else 0
                    game_number = 1
                elif st.session_state.simulated_mode == "Match Entry Without Result (Date and Teams Only)":
                    home_score = 0
                    away_score = 0
                    game_number = 1
                else:  # Date-Only mode
                    home_score = 0
                    away_score = 0
                    game_number = ""  # leave blank

                simulated_match = {
                    "date": sim_date,
                    "team": selected_team,
                    "opponent": opponent,
                    "result": expanded,
                    "WL": result_input if result_input in ["W", "L"] else "",
                    "attendance": 0,
                    "contest": 0,
                    "home_score": home_score,
                    "away_score": away_score,
                    "game_number": game_number,
                    "location": "" if (st.session_state.simulated_mode == "Date-Only Entry (Auto-generate schedule)" or home_or_away == "Not Specified") else home_or_away,
                    "auto_generate": st.session_state.simulated_mode.startswith("Date-Only")
                }
                st.session_state.simulated_matches.append(simulated_match)
                # Only reorder (and recalc game_number) for the first two modes:
                if st.session_state.simulated_mode != "Date-Only Entry (Auto-generate schedule)":
                    st.session_state.simulated_matches = order_simulated_matches(
                        st.session_state.simulated_matches, ascending=True
                    )
                st.success(f"Added match on {sim_date}")

        # Display & Delete
        if st.session_state.simulated_matches:
            st.subheader("Simulated Matches")
            sim_df = pd.DataFrame(st.session_state.simulated_matches)
            st.dataframe(sim_df)
            idx = st.selectbox(
                "Delete match",
                range(len(sim_df)),
                format_func=lambda i: f"{sim_df.loc[i,'date']} | {sim_df.loc[i,'opponent']}"
            )
            if st.button("Delete"):
                st.session_state.simulated_matches.pop(idx)
                if st.session_state.simulated_mode != "Date-Only Entry (Auto-generate schedule)":
                    st.session_state.simulated_matches = order_simulated_matches(
                        st.session_state.simulated_matches, ascending=True
                    )
                st.success("Deleted")

        # Run Season
        st.header("Run Simulated Season")
        if st.button("Run Simulated Season"):
            if st.session_state.simulated_matches:
                sim_df = pd.DataFrame(st.session_state.simulated_matches)
                combined = pd.concat([filtered_season, sim_df], ignore_index=True)
            else:
                combined = filtered_season.copy()
            combined = order_combined_season(combined)
            combined.to_csv("data/combined_simulated_season.csv", index=False)
            st.success("Combined season saved")
            st.dataframe(combined)

            # Full Match Mode
            if st.session_state.simulated_mode == "Full Match Entry (Date, Teams, and Result)":
                proc = subprocess.run(
                    ["python", "scripts/full_match_mode/full_match_entry.py", "data/combined_simulated_season.csv"],
                    capture_output=True, text=True
                )
                if proc.returncode != 0:
                    st.error(proc.stderr)
                else:
                    dfp = pd.read_csv("scripts/full_match_mode/data/processed_result.csv")
                    if "npi" in dfp.columns:
                        st.table(dfp.sort_values("npi", ascending=False)[["team", "npi"]])
                    else:
                        st.dataframe(dfp)

            # No-Result Mode
            elif st.session_state.simulated_mode == "Match Entry Without Result (Date and Teams Only)":
                proc = subprocess.run(
                    ["python", "scripts/no_result_mode/no_results_entry.py",
                     "data/combined_simulated_season.csv", str(elo_num_simulations)],
                    capture_output=True, text=True
                )
                if proc.returncode != 0:
                    st.error(proc.stderr)
                else:
                    dfp = pd.read_csv("scripts/no_result_mode/data/processed_result.csv")
                    st.dataframe(dfp)
                    # Plot
                    row = dfp[dfp.team == selected_team]
                    if not row.empty:
                        cols = [c for c in dfp.columns if c.startswith("npi_")]
                        vals = row[cols].iloc[0].astype(float).tolist()
                        fig, ax = plt.subplots()
                        ax.hist(vals, density=True)
                        ax.set_title(f"NPI Distribution for {selected_team}")
                        ax.set_xlabel("NPI")
                        ax.set_ylabel("Probability density")
                        st.pyplot(fig)

            # Date-Only Mode
            elif st.session_state.simulated_mode == "Date-Only Entry (Auto-generate schedule)":
                st.info("Processing date-only entries with external process...")
                proc = subprocess.run(
                    ["python",
                     "scripts/date_only_mode/date_only_entry.py",
                     "data/combined_simulated_season.csv",
                     str(schedule_num_simulations),
                     str(elo_num_simulations)],
                    capture_output=True, text=True
                )
                if proc.returncode != 0:
                    st.error(proc.stderr)
                else:
                    st.success("External date-only process completed successfully!")

                    # NEW: read and plot ALL merged-NPI CSVs
                from pathlib import Path

                # point at your npis folder
                npi_folder = Path("scripts/date_only_mode/result/npis")
                npi_files = sorted(
                    npi_folder.glob("schedule_*_npi.csv"),
                    key=lambda p: int(p.stem.split("_")[1])
                )

                for sched_idx, npi_file in enumerate(npi_files, start=1):
                    df_npi = pd.read_csv(npi_file)
                    st.subheader(f"NPI Results for Schedule #{sched_idx}")
                    st.dataframe(df_npi)

                    # extract this team’s NPIs
                    team_row = df_npi[df_npi['team'] == selected_team]
                    if team_row.empty:
                        st.warning(f"No NPI data for {selected_team} in {npi_file.name}")
                        continue

                    npi_cols = sorted(
                        [c for c in df_npi.columns if c.startswith("npi_")],
                        key=lambda c: int(c.split("_")[1])
                    )
                    vals = team_row[npi_cols].iloc[0].astype(float).tolist()

                    fig, ax = plt.subplots()
                    ax.hist(vals, bins='auto', density=True)
                    ax.set_title(f"Schedule {sched_idx}: NPI Distribution for {selected_team}")
                    ax.set_xlabel("NPI")
                    ax.set_ylabel("Probability Density")
                    st.pyplot(fig)