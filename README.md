# 🏐 NCAA Division III Women’s Volleyball Simulator

A data‑driven simulation platform for NCAA Division III Women’s Volleyball.  
Developed by **Yilin Du** (UI and NPI calculation) and **Fletcher Sun** (ELO simulation and schedule auto-generation)  
Under the guidance of **Prof. Ron Yurko** at **Carnegie Mellon University**.  
Parts of the NPI calculation are adapted from the **D3 Datacast** team.

---

## 🎯 Overview

This simulator enables season simulations for NCAA Division III Women’s Volleyball teams.

---

## 🚦 Simulation Modes

The simulator supports **three input modes**:

1. **Full Entry**:  
   Requires: `Date`, `Opponent`, `Result`

2. **Entry Without Result**:  
   Requires: `Date`, `Opponent`

3. **Data-Only Entry**:  
   Requires: `Date` only

---

## 🧮 How It Works

All simulations require a **base season**, which contains all matches of a given season.  
> ⚠️ *Matches do not have to be real but it affects the result of the simulation.*

The base season is used to calculate team NPIs, which depend on full-season context.

---

## 📄 Input Format Example

```csv
date,team,opponent,result,attendance,contest,WL,home_score,away_score,game_number
08/30/2024,Alfred St.,Smith,L 1-3,46.0,5667720,L,1,3,1
08/30/2024,Hilbert,Thiel,L 1-3,35.0,5667545,L,1,3,1
08/30/2024,Mount Aloysius,Swarthmore,L 0-3,85.0,5667553,L,0,3,1
```

> **Note:** Fields of `attendance`, `contest`, and `game_number` are optional.

---

## 🔧 Simulation Configuration (Mode 2 & 3)

- **Number of Schedule Simulations** (Mode 3 only):  
  How many different schedules to randomly generate for the selected team.

- **Number of ELO Simulations** (Mode 2 & 3):  
  How many times the ELO system should simulate outcomes for a given schedule.

---

## 🎯 Team Selection & Match Entry

- **Select a Team**:  
  Choose the target team. Matches involving this team will be removed from the base season.

- **Add Matches**:  
  Add match entries manually. The "team" field should match the selected team above.

---

## ✅ When You’re Ready

Once data and simulation parameters are set:  
**Click "Run Simulation"** to begin analysis!

---

## 📦 Requirements

Install required packages:

```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Web Interface

To launch the local Streamlit UI:

```bash
streamlit run interface.py
```

---
