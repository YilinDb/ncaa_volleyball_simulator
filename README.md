NCAA Division III Women’s Volleyball Simulator

A data‑driven simulation platform for NCAA Division III women’s volleyball. Built by Yilin Du (UI and NPI calculation) and Fletcher Sun (elo simulation and schedule auto-generation) under the guidance of Prof. Ron Yurko at Carnegie Mellon University. Portions of the NPI calculation algorithm are adapted from the work of D3 Datacast team.

The simulator has three modes:

All simulations require a base season to run. This base season has all matches of a season. The matches does not need to be real matches but what the base season affect the simulation result. and should allow the simulator to calculate NPI, especially NPI for other teams.

It should has a format like below:
date,team,opponent,result,attendance(NOT REQUIRED),contest(NOT REQUIRED),WL,home_score,away_score,game_number(NOT REQUIRED)
08/30/2024,Alfred St.,Smith,L 1-3,46.0,5667720,L,1,3,1
08/30/2024,Hilbert,Thiel,L 1-3,35.0,5667545,L,1,3,1
08/30/2024,Mount Aloysius,Swarthmore,L 0-3,85.0,5667553,L,0,3,1

1. full-entry
2. entry without result
3. data-only entry



Required packages:
See requirements.txt

Run the Web UI Locally:
streamlit run interface.py
