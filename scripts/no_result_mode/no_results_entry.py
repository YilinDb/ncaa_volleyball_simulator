# src/myapp/main.py
import time
import sys
import pandas as pd
from pathlib import Path

from load_games import load_games
from load_teams import load_teams
from process_games_iteration import process_games_iteration
from save_npi_results_to_csv import save_npi_results_to_csv
from elo_simulation import predict_result

def main(data_path, num_elo_iteration):
    """Main entry point for the application."""
    NUM_ITERATIONS = 30
    elo_base_path = "scripts/no_result_mode/data/elo_start_25.csv"
    elo_base = pd.read_csv(elo_base_path)
    schedule = pd.read_csv(data_path)

    npi_results = []
    for sim in range(num_elo_iteration):
        data = predict_result(elo_base, schedule, scaling_factor=400, update_factor=133)
        try:
            valid_teams = load_teams(data)
            games = load_games(data, valid_teams)
            start_total_time = time.time()
            # Initialize once
            opponent_npis = {team_id: 50 for team_id in valid_teams}
            final_teams = None
            total_games = 0

            for i in range(NUM_ITERATIONS):
                iteration_number = i + 1
                
                teams = process_games_iteration(
                    games, valid_teams, opponent_npis, iteration_number
                )

                if iteration_number == NUM_ITERATIONS:
                    final_teams = teams

                    # Calculate total games in final iteration
                    for team_id, team_data in teams.items():
                        total_games += len(team_data["all_game_npis"])

                # Update in place for next iteration
                opponent_npis.clear()
                opponent_npis.update(
                    {
                        team_id: stats["npi"]
                        for team_id, stats in teams.items()
                        if stats["has_games"]
                    }
                )

            total_time = time.time() - start_total_time
            print(f"\nTotal processing time: {total_time:.3f} seconds")
            print(f"Average time per iteration: {total_time/NUM_ITERATIONS:.3f} seconds")
            print(f"Total number of games in the data: {len(games)}")
            print(f"Total number of games processed in the final iteration: {total_games}")

            final_teams_df = pd.DataFrame([
                {"team": team, f"npi_{sim}": stats.get("npi", None)}
                for team, stats in final_teams.items()
            ])
            npi_results.append(final_teams_df)

        except Exception as e:
            print(f"Error processing: {e}")
            raise
    
    merged_sim_df = npi_results[0]
    for sim_df in npi_results[1:]:
        merged_sim_df = pd.merge(merged_sim_df, sim_df, on="team", how="outer")
    
    # Save the final result to a CSV file.
    output_path = Path(__file__).parent / "data" / "processed_result.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged_sim_df.to_csv(output_path, index=False)
    print(f"Final simulation results saved to {output_path}")
    
    return merged_sim_df

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process_full_matches.py <path_to_csv>")
        sys.exit(1)
    csv_path = sys.argv[1]
    num_elo_iteration = int(sys.argv[2])

    main(csv_path, num_elo_iteration)
