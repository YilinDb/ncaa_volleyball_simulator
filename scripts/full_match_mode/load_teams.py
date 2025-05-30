import csv

def load_teams(csv_file_path):
    teams = {}
    # Open the CSV file; assume the first row is the header.
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Extract team names from both the 'team' and 'opponent' columns.
            team_name = row["team"].strip()
            opponent_name = row["opponent"].strip()
            
            # Use the team name as both the key and value.
            if team_name not in teams:
                teams[team_name] = team_name
            if opponent_name not in teams:
                teams[opponent_name] = opponent_name

    print(f"Loaded {len(teams)} teams from {csv_file_path}")
    return teams

'''
def load_teams(base_path, year):
    teams = {}
    year_str = str(year)
    teams_path = base_path / year_str / "teams.txt"
    mapping_path = base_path / year_str / "teams_mapping.txt"

    try:
        with open(teams_path, "r") as file:
            for line in file:
                try:
                    team_id, team_name = line.strip().split(",", 1)
                    teams[team_id.strip()] = team_name.strip()
                except Exception as e:
                    continue
        print(f"Loaded {len(teams)} teams from {year_str}/teams.txt")
    except FileNotFoundError:
        print(f"Warning: Could not find teams file at {teams_path}")
        return teams

    mapping_count = 0
    try:
        with open(mapping_path, "r") as file:
            for line in file:
                try:
                    parts = line.strip().split(",")
                    if len(parts) >= 3:
                        team_id = parts[0].strip()
                        mapped_name = parts[2].strip()
                        if team_id in teams:
                            teams[team_id] = mapped_name
                            mapping_count += 1
                except Exception as e:
                    continue
        print(
            f"Applied {mapping_count} name mappings from {year_str}/teams_mapping.txt"
        )
    except FileNotFoundError:
        print(f"Warning: Could not find mapping file at {mapping_path}")

    return teams
'''
