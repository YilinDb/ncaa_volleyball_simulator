# src/myapp/main.py
import sys
import time
import pandas as pd
from pathlib import Path

from load_games import load_games
from load_teams import load_teams
from process_games_iteration import process_games_iteration
from elo_simulation import predict_result
from schedule_generator import fill_schedule

def main(data_path, num_elo_iteration, num_schedule_simulations):
    NUM_ITERATIONS    = 30
    elo_base_path     = "scripts/no_result_mode/data/elo_start_25.csv"
    elo_base          = pd.read_csv(elo_base_path)
    schedule_template = pd.read_csv(data_path, index_col=False)

    # Base result folder for date‑only mode
    result_base   = Path(__file__).parent / "result"
    schedules_dir = result_base / "schedules"
    npi_dir       = result_base / "npis"

    # Ensure both folders exist and are emptied
    for d in (schedules_dir, npi_dir):
        if d.exists():
            for f in d.iterdir():
                if f.is_file():
                    f.unlink()
        else:
            d.mkdir(parents=True, exist_ok=True)

    for sched in range(num_schedule_simulations):
        print(f"\n=== Running schedule simulation {sched+1}/{num_schedule_simulations} ===")

        # 1) generate & fix one schedule
        schedule = fill_schedule(schedule_template, elo_base)

        # 2) save raw schedule CSV
        schedule_csv = schedules_dir / f"schedule_{sched+1}.csv"
        schedule.to_csv(schedule_csv, index=False)
        print(f"Saved raw schedule → {schedule_csv}")

        # 3) run the Elo sims on that schedule
        npi_dfs = []
        for sim in range(num_elo_iteration):
            data = predict_result(
                elo_base,
                schedule,
                scaling_factor=400,
                update_factor=133
            )
            valid_teams = load_teams(data)
            games       = load_games(data, valid_teams)

            opponent_npis = {t: 50 for t in valid_teams}
            final_teams   = None
            start = time.time()
            for i in range(NUM_ITERATIONS):
                teams = process_games_iteration(
                    games, valid_teams, opponent_npis, i+1
                )
                if i+1 == NUM_ITERATIONS:
                    final_teams = teams
                opponent_npis = {
                    tid: stats["npi"]
                    for tid, stats in teams.items()
                    if stats["has_games"]
                }
            print(f"  Elo sim {sim+1} done in {time.time()-start:.2f}s")

            npi_dfs.append(pd.DataFrame([
                {"team": team, f"npi_{sim+1}": stats.get("npi")}
                for team, stats in final_teams.items()
            ]))

        # 4) merge all Elo‐simulation DataFrames for this schedule
        merged = npi_dfs[0]
        for df_sim in npi_dfs[1:]:
            merged = pd.merge(merged, df_sim, on="team", how="outer")

        # 5) save merged NPI results CSV
        npi_csv = npi_dir / f"schedule_{sched+1}_npi.csv"
        merged.to_csv(npi_csv, index=False)
        print(f"Saved merged NPIs → {npi_csv}")

    print("All schedule simulations complete.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python main.py <path_to_csv> <num_elo_iteration> <num_schedule_simulations>")
        sys.exit(1)
    csv_path = sys.argv[1]
    num_elo_iter = int(sys.argv[2])
    num_sched_sims = int(sys.argv[3])
    main(csv_path, num_elo_iter, num_sched_sims)
