# AI-VS-WATER
This repository supports the research article:
'**Balancing population demand and water stress in data centre siting under climate change: A UK spatial optimisation study**' by Allen, J. and Herrera, M. (2026); Submitted to the AQUA – Water Infrastructure, Ecosystems and Society (under review)

# **Overview**
As the UK data centre sector expands under increasing AI demand, siting decisions must account for long-term hydrological risk under climate change. This repository provides the code, data, excels, and spatial outputs used in a multi-objective facility location optimisation study across England (2026–2100). The model balances population coverage against water stress across 295 Local Authority Districts, using a bespoke Water Resilience Index (WRI) derived from Met Office, BGS, and Environment Agency hydrological datasets.

<img width="597" height="801" alt="image" src="https://github.com/user-attachments/assets/a7f76b32-3892-4e7d-9577-b7678453cf3f" />

# **Repository Structure**
```
ArcGIS Maps/
├── F4.1 Population Map.pdf                    # LAD population distribution map
├── F4.2 Advanced Population Map.pdf           # Weighted population coverage map
├── F4.3 Water Resilience Index Map.pdf        # Spatial WRI scores across England
├── F5.3 Temporal Shift.pdf                    # Optimal site shift 2026–2100
├── F5.4 District Selection Frequency.pdf      # LAD selection frequency across frontier
├── F5.5 Recommended Data Centre by Option.pdf # Options A/B/C spatial comparison
└── F5.6 Capping Map.pdf                       # k-capping sensitivity map

Code/
└── Code Used to Generate Results/
    ├── Solve Python/
    │   ├── solve.py                           # 2026 epsilon-constraint optimisation
    │   ├── solve_2050.py                      # 2050 scenario optimisation
    │   ├── solve_2075.py                      # 2075 scenario optimisation
    │   └── solve_2100.py                      # 2100 scenario optimisation
    ├── Build Python/
    │   ├── build_excel.py                     # 2026 Pareto frontier output builder
    │   ├── build_excel_2050.py                # 2050 Pareto frontier output builder
    │   ├── build_excel_2075.py                # 2075 Pareto frontier output builder
    │   └── build_excel_2100.py                # 2100 Pareto frontier output builder
    └── Json Files Produced Via Solve Python/
        ├── pareto_results.json                # 2026 raw Pareto frontier data
        ├── pareto_results_2050.json           # 2050 raw Pareto frontier data
        ├── pareto_results_2075.json           # 2075 raw Pareto frontier data
        └── pareto_results_2100.json           # 2100 raw Pareto frontier data

Graphs/
├── All Pareto Frontier Graphs/
│   ├── 2026 Pareto Frontier.pdf              # Full 2026 Pareto frontier plot
│   ├── 2050 Pareto Frontier.pdf              # Full 2050 Pareto frontier plot
│   ├── 2075 Pareto Frontier.pdf              # Full 2075 Pareto frontier plot
│   └── 2100 Pareto Frontier.pdf              # Full 2100 Pareto frontier plot
├── F5.1 Pareto Frontier 2026 Baseline.pdf    # Annotated baseline frontier
├── F5.2 Temporal Shift of the k=10 Pareto Frontier.pdf  # k=10 shift over time
├── F5.7 Min Stress Max Population.pdf        # Extreme solution comparison
└── F5.9 Sensitivity Analysis.pdf             # WRI weighting sensitivity results

Results/
├── dc_optimisation_results.xlsx              # 2026 full Pareto solution set
├── dc_optimisation_results_2050.xlsx         # 2050 full Pareto solution set
├── dc_optimisation_results_2075.xlsx         # 2075 full Pareto solution set
└── dc_optimisation_results_2100.xlsx         # 2100 full Pareto solution set
```

# **Optimisation Model**
The model applies an epsilon-constraint method to solve a bi-objective facility location problem, treating population coverage as the primary objective and water stress as an epsilon-constrained secondary objective. Implemented in Python using PuLP (CBC solver) with 100 epsilon steps across a Pareto frontier. Three reference solutions (Options A, B, C) are extracted representing low, balanced, and high water-resilience siting strategies. Scenarios are solved independently for 2026, 2050, 2075, and 2100 under UKCP18-aligned climate projections.
# **Spatial Framework**
Spatial processing was conducted in ArcGIS Pro, joining hydrological datasets from the Met Office HadUK grid, BGS hydrogeology classifications, and EA Q95 low-flow data to 295 English Local Authority District boundaries. The WRI (Water Resilience Index) is computed as an arithmetic mean of the three normalised sub-indices and inverted for use as a minimisation constraint in the optimisation model.
# **Requirements**
- Python 3.x
- PuLP
- pandas
- numpy
- matplotlib
- openpyxl
- ArcGIS Pro (for spatial pre-processing)
