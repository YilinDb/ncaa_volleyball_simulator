import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
import math


def calculate_expected_score(team_rating, opp_team_rating, scaling_factor=400):
    """Calculate expected score based on ELO formula."""
    return 1 / (1 + 10 ** ((opp_team_rating - team_rating) / scaling_factor))

def calculate_new_rating(team_rating, observed_score, expected_score, update_factor=20):
    """Update ELO rating based on the expected and actual scores."""
    return team_rating + update_factor * (observed_score - expected_score)

def calculate_elo(elo_table, data, scaling_factor=400, update_factor=20):
    """Update ELO ratings based on match results."""
    for _, game in data.iterrows():
        home_team = game['team']
        away_team = game['opponent']
        WL = 1 if game['WL'] == "W" else 0  # 1 for win, 0 for loss
        

        # Add game played
        elo_table.loc[elo_table['team'] == home_team, 'games'] += 1
        elo_table.loc[elo_table['team'] == away_team, 'games'] += 1

        # Add win count
        if WL == 1:
            elo_table.loc[elo_table['team'] == home_team, 'wins'] += 1
        else:
            elo_table.loc[elo_table['team'] == away_team, 'wins'] += 1

        # Get current ELO ratings
        home_rating = elo_table.loc[elo_table['team'] == home_team, 'elo_rating'].values[0]
        away_rating = elo_table.loc[elo_table['team'] == away_team, 'elo_rating'].values[0]

        #get expected home win
        expected_win = calculate_expected_score(home_rating, away_rating, scaling_factor)

        # Calculate new ratings
        new_home_rating = calculate_new_rating(home_rating, WL, 
                                               expected_win,
                                               update_factor)
        new_away_rating = calculate_new_rating(away_rating, 1 - WL, 
                                               1-expected_win,
                                               update_factor)

        # Update ELO ratings
        elo_table.loc[elo_table['team'] == home_team, 'elo_rating'] = new_home_rating
        elo_table.loc[elo_table['team'] == away_team, 'elo_rating'] = new_away_rating

    return elo_table


def predict_result(elo_table, data, scaling_factor=400, update_factor=20):
    #add prediction column to data
    data['predicted_WL'] = "W"

    for i, game in data.iterrows():
        home_team = game['team']
        away_team = game['opponent']

        # Add game played
        elo_table.loc[elo_table['team'] == home_team, 'games'] += 1
        elo_table.loc[elo_table['team'] == away_team, 'games'] += 1

        # Get current ELO ratings
        home_rating = elo_table.loc[elo_table['team'] == home_team, 'elo_rating'].values[0]
        away_rating = elo_table.loc[elo_table['team'] == away_team, 'elo_rating'].values[0]

        #determine who will win
        expected_win = calculate_expected_score(home_rating, away_rating, scaling_factor)
        WL =  np.random.binomial(n=1, p=expected_win)
        #print(WL)

        # Add predicted count
        data.loc[i, 'WL'] = "W" if WL == 1 else "L"

        # change the score
        data.at[i, 'home_score'] = 1 if WL == 1 else 0
        data.at[i, 'away_score'] = 0 if WL == 1 else 1

        # Add win count
        if WL == 1:
            elo_table.loc[elo_table['team'] == home_team, 'wins'] += 1
        else:
            elo_table.loc[elo_table['team'] == away_team, 'wins'] += 1

        # Calculate new ratings
        new_home_rating = calculate_new_rating(home_rating, WL, 
                                               expected_win,
                                               update_factor)
        new_away_rating = calculate_new_rating(away_rating, 1 - WL, 
                                               1- expected_win,
                                               update_factor)

        # Update ELO ratings
        elo_table.loc[elo_table['team'] == home_team, 'elo_rating'] = new_home_rating
        elo_table.loc[elo_table['team'] == away_team, 'elo_rating'] = new_away_rating

    return data


def train_update_factor(elo_table, data, scaling_factor=400, update_factor=20):
    #add prediction column to data
    data['predicted_Expected_win'] = 0.0
    data['square_error'] = 0.0
    data['predicted_WL'] = "W"
    data['home_elo'] = 0.0
    data['away_elo'] = 0.0

    for i, game in data.iterrows():
        home_team = game['team']
        away_team = game['opponent']

        # Add game played
        elo_table.loc[elo_table['team'] == home_team, 'games'] += 1
        elo_table.loc[elo_table['team'] == away_team, 'games'] += 1

        # Get current ELO ratings
        home_rating = elo_table.loc[elo_table['team'] == home_team, 'elo_rating'].values[0]
        away_rating = elo_table.loc[elo_table['team'] == away_team, 'elo_rating'].values[0]
        data.loc[i, 'home_elo'] = home_rating 
        data.loc[i, 'away_elo'] = away_rating

        #determine who will win
        expected_win = calculate_expected_score(home_rating, away_rating, scaling_factor)
        Predicted_WL =  np.random.binomial(n=1, p=expected_win)
        data.loc[i, 'predicted_WL'] = Predicted_WL
        #print(WL)

        # Add expected win
        data.loc[i, 'predicted_Expected_win'] = expected_win

        #calculate error
        WL = 1 if game['WL'] == "W" else 0 
        data.loc[i, 'square_error'] = (WL-expected_win)**2

        # Add win count
        if WL == 1:
            elo_table.loc[elo_table['team'] == home_team, 'wins'] += 1
        else:
            elo_table.loc[elo_table['team'] == away_team, 'wins'] += 1

        # Calculate new ratings
        new_home_rating = calculate_new_rating(home_rating, WL, 
                                               expected_win,
                                               update_factor)
        new_away_rating = calculate_new_rating(away_rating, 1 - WL, 
                                               1- expected_win,
                                               update_factor)

        # Update ELO ratings
        elo_table.loc[elo_table['team'] == home_team, 'elo_rating'] = new_home_rating
        elo_table.loc[elo_table['team'] == away_team, 'elo_rating'] = new_away_rating

    return data

def calculate_error(schedule):
    return (schedule['WL'] != schedule['predicted_WL']).mean()

def cross_season(elo_table, P = 0.5):
    elo_table['elo_rating'] = elo_table['elo_rating']*P + (1-P)*1505
    return elo_table

def predict_new_schedule(schedule, prev_elo_path, schedule_path):
    elo_24 = pd.read_csv(prev_elo_path)
    data24  = pd.read_csv(schedule_path)
    elo_after_23 =  calculate_elo(elo_24, data24, scaling_factor=400, update_factor=133)
    elo_start_24 = cross_season(elo_after_23, P = 0.8)
    predicted_schedule = predict_result(elo_start_24, schedule, scaling_factor=400, update_factor=133)
    return predicted_schedule 

#FINAL PARAMETER P = 0.8, UPDATE_FACTOR = 133
#start with after 24 season after cross-season regression