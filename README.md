# AI-VS-WATER
This repository supports the research article:
'**Balancing population demand and water stress in data centre siting under climate change: A UK spatial optimisation study**' by Allen, J. and Herrera, M. (2026); Submitted to the AQUA – Water Infrastructure, Ecosystems and Society (under review)

# **Overview**
As the UK data centre sector expands under increasing AI demand, siting decisions must account for long-term hydrological risk under climate change. This repository provides the code, data, excels, and spatial outputs used in a multi-objective facility location optimisation study across England (2026–2100). The model balances population coverage against water stress across 295 Local Authority Districts, using a bespoke Water Resilience Index (WRI) derived from Met Office, BGS, and Environment Agency hydrological datasets.

<img width="597" height="801" alt="image" src="https://github.com/user-attachments/assets/a7f76b32-3892-4e7d-9577-b7678453cf3f" />
# **Repository Structure**

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
