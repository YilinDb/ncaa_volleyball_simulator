import pandas as pd

def load_games(df, valid_teams):
    games = []
    seen_games = set()
    zero_zero_count = 0
    duplicate_count = 0
    skipped_due_to_invalid_teams = 0

    # Clean column names in case of extra whitespace.
    df.columns = df.columns.str.strip()

    for _, row in df.iterrows():
        try:
            # Extract and clean fields from the DataFrame.
            game_date = row["date"].strip()
            team1_id = row["team"].strip()        # Home team as team1
            team2_id = row["opponent"].strip()      # Opponent as team2
            # Convert scores to integer.
            team1_score = int(row["home_score"])
            team2_score = int(row["away_score"])
            game_number = int(row["game_number"])

            # Skip games where both scores are zero.
            if team1_score == 0 and team2_score == 0:
                zero_zero_count += 1
                continue

            # Skip games where either team is not in valid_teams.
            if team1_id not in valid_teams or team2_id not in valid_teams:
                skipped_due_to_invalid_teams += 1
                continue

            # Create a unique game identifier: sorted team IDs + date + game_number.
            game_id = tuple(sorted([team1_id, team2_id]) + [game_date, game_number])
            if game_id in seen_games:
                duplicate_count += 1
                continue

            seen_games.add(game_id)
            # NEW: Return keys expected by downstream code ("team1_score", "team2_score") 
            games.append({
                "date": game_date,
                "team1_id": team1_id,
                "team2_id": team2_id,
                "team1_score": team1_score,
                "team2_score": team2_score 
            })
        except Exception as e:
            # Optionally log the error for debugging.
            continue
    print("Game Loading Statistics:")
    print(f"Total games loaded: {len(games)}")
    print(f"Skipped 0-0 games: {zero_zero_count}")
    print(f"Skipped duplicates: {duplicate_count}")
    print(f"Skipped due to invalid teams: {skipped_due_to_invalid_teams}")

    return games

'''
def load_games(base_path, year, valid_teams, use_season_results=False):
    games = []
    seen_games = set()
    year_str = str(year)
    games_path = (
        base_path / year_str / "season_results.txt"
        if use_season_results
        else base_path / year_str / "games.txt"
    )
    zero_zero_count = 0
    duplicate_count = 0
    skipped_due_to_invalid_teams = 0

    try:
        with open(games_path, "r") as file:
            for line in file:
                try:
                    cols = line.strip().split(",")
                    if len(cols) < 8:
                        continue

                    date = cols[0].strip()
                    team1_id = cols[2].strip()
                    team2_id = cols[5].strip()
                    team1_score = int(cols[4])
                    team2_score = int(cols[7])
                    if team1_score == 0 and team2_score == 0:
                        zero_zero_count += 1
                        continue

                    # Skip games where either team is not in the valid_teams dictionary
                    if team1_id not in valid_teams or team2_id not in valid_teams:
                        skipped_due_to_invalid_teams += 1
                        continue

                    # Create a unique game identifier (ordered team IDs + date)
                    game_id = tuple(sorted([team1_id, team2_id]) + [date])

                    # Skip duplicates
                    if game_id in seen_games:
                        duplicate_count += 1
                        continue

                    seen_games.add(game_id)
                    games.append(
                        {
                            "date": date,
                            "team1_id": team1_id,
                            "team2_id": team2_id,
                            "team1_score": team1_score,
                            "team2_score": team2_score,
                        }
                    )

                except Exception as e:
                    continue

        print(f"Game Loading Statistics:")
        print(f"Total games loaded: {len(games)}")
        print(f"Skipped 0-0 games: {zero_zero_count}")
        print(f"Skipped duplicates: {duplicate_count}")
        print(f"Skipped due to invalid teams: {skipped_due_to_invalid_teams}")

    except Exception as e:
        print(f"Error loading games: {e}")

    return games
'''
