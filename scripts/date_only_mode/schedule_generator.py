import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import math
import random

def fix_game_number(schedule):
    df = schedule.copy()
    # Within each (date, team, opponent) group, assign 1,2,3… in the original row‐order:
    df['game_number'] = df.groupby(
        ['date','team','opponent'], 
        sort=False
    ).cumcount().add(1)
    return df

#Schedule
#Formatted schedule without CMU as panda df

#Date
#List of dates of ordered play game with length num_games. Dates should be formatted as "MM/DD/YYYY", there can be duplicate

#num_games 
# total number of games to be played

#elo_table
#formatted elo table


#strategy terms:
# 0 = random or anything else
# 1 = 50% top 1/3 teams, random for the rest
# 2 = 50% middle 1/3 teams, random for the rest
# 3 = 50% list 1/3 teams, random for the rest

def generate_schedule(schedule, elo_table, dates, num_games, strategy):

    if len(dates) != num_games:
        raise ValueError(f"Numebr of games should be the same as length of the date list.")

    UAA = ["CWRU", "Brandeis", "Carnegie Mellon", "Emory", "NYU", "UChicago", "Rochester (NY)", "WashU"]
    in_region = ["CWRU", "Hope", "Carnegie Mellon", "Marietta", "Calvin", "Otterbein", "Ohio Northern"]
    in_region_count = num_games*0.7
    home = "Carnegie Mellon"
    elo_sorted = elo_table.sort_values(by="elo_rating", ascending=True).reset_index(drop=True)
    bottom, middle, top = np.array_split(elo_sorted, 3)



    if strategy == 1:        
        for i in range(0, num_games):
            if i < in_region_count:
                #fulfill in region requirement first
                away = random.sample(in_region)[0]
            else:
                #then pick from top teams
                away = top['team'].sample().values[0]
            game = {"date": dates[i],"team": home,"opponent": away,"game_number":1}
            schedule  = pd.concat([schedule, pd.DataFrame([game])], ignore_index=True)
        
        #fix gamenumber, sort and return
        schedule = fix_game_number(schedule)
        schedule = schedule.sort_values(by = "date")
        return schedule
    

    elif strategy == 2:
        for i in range(0, num_games):
            if i < in_region_count:
                #fulfill in region requirement first
                away = random.sample(in_region)[0]
            else:
                #then pick from middle teams
                away = middle['team'].sample().values[0]
            game = {"date": dates[i],"team": home,"opponent": away,"game_number":1}
            schedule  = pd.concat([schedule, pd.DataFrame([game])], ignore_index=True)
        
        #fix gamenumber, sort and return
        schedule = fix_game_number(schedule)
        schedule = schedule.sort_values(by = "date")
        return schedule
    

    elif strategy == 3:
        for i in range(0, num_games):
            if i < in_region_count:
                #fulfill in region requirement first
                away = random.sample(in_region)[0]
            else:
                #then pick from bottom teams
                away = bottom['team'].sample().values[0]
            game = {"date": dates[i],"team": home,"opponent": away,"game_number":1}
            schedule  = pd.concat([schedule, pd.DataFrame([game])], ignore_index=True)
        
        #fix gamenumber, sort and return
        schedule = fix_game_number(schedule)
        schedule = schedule.sort_values(by = "date")
        return schedule
    
    #random
    else:
        for i in range(0, num_games):
            if i < in_region_count:
                #play in region game first
                away = random.sample(in_region, k=1)[0]
            else:
                away = elo_table['team'].sample().values[0]
            game = {"date": dates[i],"team": home,"opponent": away,"game_number":1}
            schedule  = pd.concat([schedule, pd.DataFrame([game])], ignore_index=True)
        

        #fix gamenumber, sort and return
        schedule = fix_game_number(schedule)
        schedule = schedule.sort_values(by = "date")
        return schedule



#same as above but ignoring any in region requirement
def generate_schedule_random(schedule, elo_table, dates, num_games):
        for i in range(0, num_games):
            away = elo_table['team'].sample().values[0]
            game = {"date": dates[i],"team": "Carnegie Mellon","opponent": away,"game_number":1}
            schedule  = pd.concat([schedule, pd.DataFrame([game])], ignore_index=True)
        

        #fix gamenumber, sort and return
        schedule = fix_game_number(schedule)
        schedule = schedule.sort_values(by = "date")
        return schedule    



#fill the rows in the 
def fill_schedule(schedule, elo_table):
    for i, game in schedule.iterrows():
        #find game without opponent and add the opponent and game number
        if pd.isna(game['opponent']) or game['opponent'] == "":
            away = elo_table['team'].sample().values[0]
            schedule.loc[i, 'opponent'] = away

    # STEP 1: parse the date column
    schedule = schedule.copy()
    schedule['date'] = pd.to_datetime(schedule['date'], format="%m/%d/%Y", errors='coerce')

    # STEP 2: sort by date _and_ game_number
    # If your fix_game_number recomputes game_number correctly,
    # call it first; otherwise you can sort, then recalc game_number.
    schedule = fix_game_number(schedule)
    schedule = schedule.sort_values(['date', 'game_number']).reset_index(drop=True)

    schedule['date'] = schedule['date'].dt.strftime("%m/%d/%Y")

    return schedule

if __name__ == "__main__":
    #Testing
    test_schedule = pd.read_csv("C:/Users/Fletcher/OneDrive/桌面/Academic/NPI Capstone/24_season.csv")
    dates = ["12/12/2024", "10/26/2024"]
    elo_table = pd.read_csv("C:/Users/Fletcher/OneDrive/桌面/Academic/NPI Capstone/elo_start_25.csv")

    editted = generate_schedule(test_schedule, elo_table, dates, 2, 0)
    editted.to_csv("schedule_generation_test.csv")
