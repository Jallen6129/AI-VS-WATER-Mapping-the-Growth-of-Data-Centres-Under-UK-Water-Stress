"""
Multi-Objective Facility Location: Data Centre placement in England
Scenario: 2100 - Stress multipliers applied to penalty (post-inversion), capped at 1.0
Objectives: Maximise population served | Minimise water stress
Method: epsilon-constraint -> full Pareto frontier
"""

import pandas as pd
import numpy as np
from pulp import *
import json

# ── 1. DATA ─────────────────────────────────────────────────────────────────
# England upper-tier / unitary councils
# Water stress index: numeric score derived from EA 2021 classification
#   "Serious"  = 1.0  (highest stress)
#   "Moderate" = 0.6
#   "Low"      = 0.2
# Population: ONS Census 2021, thousands
# Geographic region included for spatial diversity analysis

councils = [
    ("Hartlepool", "North East", 0.404, 92338),
    ("Middlesbrough", "North East", 0.311, 143926),
    ("Redcar and Cleveland", "North East", 0.366, 136531),
    ("Stockton-on-Tees", "North East", 0.419, 196595),
    ("Darlington", "North East", 0.338, 107799),
    ("Halton", "North West", 0.628, 128478),
    ("Warrington", "North West", 0.548, 210974),
    ("Blackburn with Darwen", "North West", 0.488, 154738),
    ("Blackpool", "North West", 0.479, 141036),
    ("Kingston upon Hull, City of", "Yorkshire and The Humber", 0.651, 267014),
    ("East Riding of Yorkshire", "Yorkshire and The Humber", 0.424, 342215),
    ("North East Lincolnshire", "Yorkshire and The Humber", 0.433, 156966),
    ("North Lincolnshire", "Yorkshire and The Humber", 0.296, 169680),
    ("York", "Yorkshire and The Humber", 0.423, 202821),
    ("Derby", "East Midlands", 0.411, 261364),
    ("Leicester", "East Midlands", 0.391, 368571),
    ("Rutland", "East Midlands", 0.33, 41049),
    ("Nottingham", "East Midlands", 0.454, 323632),
    ("Herefordshire, County of", "West Midlands", 0.429, 187034),
    ("Telford and Wrekin", "West Midlands", 0.301, 185541),
    ("Stoke-on-Trent", "West Midlands", 0.452, 258366),
    ("Bath and North East Somerset", "South West", 0.34, 193409),
    ("Bristol, City of", "South West", 0.495, 472465),
    ("North Somerset", "South West", 0.34, 216726),
    ("South Gloucestershire", "South West", 0.391, 290424),
    ("Plymouth", "South West", 0.476, 264695),
    ("Torbay", "South West", 0.517, 139324),
    ("Swindon", "South West", 0.196, 233407),
    ("Peterborough", "East of England", 0.265, 215671),
    ("Luton", "East of England", 0.385, 225262),
    ("Southend-on-Sea", "East of England", 0.318, 180686),
    ("Thurrock", "East of England", 0.372, 176001),
    ("Medway", "South East", 0.349, 279773),
    ("Bracknell Forest", "South East", 0.216, 124607),
    ("West Berkshire", "South East", 0.181, 161448),
    ("Reading", "South East", 0.163, 174224),
    ("Slough", "South East", 0.196, 158500),
    ("Windsor and Maidenhead", "South East", 0.186, 153496),
    ("Wokingham", "South East", 0.22, 177503),
    ("Milton Keynes", "South East", 0.139, 287060),
    ("Brighton and Hove", "South East", 0.291, 277103),
    ("Portsmouth", "South East", 0.286, 208003),
    ("Southampton", "South East", 0.413, 248922),
    ("Isle of Wight", "South East", 0.369, 140459),
    ("County Durham", "North East", 0.409, 522068),
    ("Cheshire East", "North West", 0.466, 398772),
    ("Cheshire West and Chester", "North West", 0.476, 357150),
    ("Shropshire", "West Midlands", 0.331, 323606),
    ("Cornwall", "South West", 0.446, 570305),
    ("Wiltshire", "South West", 0.352, 510333),
    ("Bedford", "East of England", 0.142, 185225),
    ("Central Bedfordshire", "East of England", 0.176, 294252),
    ("Northumberland", "North East", 0.486, 320567),
    ("Bournemouth, Christchurch and Poole", "South West", 0.447, 400196),
    ("Dorset", "South West", 0.447, 379579),
    ("Buckinghamshire", "South East", 0.181, 553078),
    ("North Northamptonshire", "East Midlands", 0.18, 359525),
    ("West Northamptonshire", "East Midlands", 0.264, 425725),
    ("Cumberland", "North West", 0.512, 273257),
    ("Westmorland and Furness", "North West", 0.479, 226592),
    ("North Yorkshire", "Yorkshire and The Humber", 0.394, 615491),
    ("Somerset", "South West", 0.417, 571548),
    ("Cambridge", "East of England", 0.281, 145674),
    ("East Cambridgeshire", "East of England", 0.222, 87762),
    ("Fenland", "East of England", 0.163, 102462),
    ("Huntingdonshire", "East of England", 0.186, 180832),
    ("South Cambridgeshire", "East of England", 0.254, 162118),
    ("Amber Valley", "East Midlands", 0.395, 126206),
    ("Bolsover", "East Midlands", 0.31, 80272),
    ("Chesterfield", "East Midlands", 0.535, 103569),
    ("Derbyshire Dales", "East Midlands", 0.291, 71540),
    ("Erewash", "East Midlands", 0.491, 112906),
    ("High Peak", "East Midlands", 0.303, 90933),
    ("North East Derbyshire", "East Midlands", 0.397, 102001),
    ("South Derbyshire", "East Midlands", 0.461, 107205),
    ("East Devon", "South West", 0.53, 150828),
    ("Exeter", "South West", 0.493, 130709),
    ("Mid Devon", "South West", 0.489, 82852),
    ("North Devon", "South West", 0.472, 98611),
    ("South Hams", "South West", 0.482, 88627),
    ("Teignbridge", "South West", 0.533, 134803),
    ("Torridge", "South West", 0.503, 68114),
    ("West Devon", "South West", 0.425, 57096),
    ("Eastbourne", "South East", 0.267, 101686),
    ("Hastings", "South East", 0.379, 90995),
    ("Lewes", "South East", 0.27, 99905),
    ("Rother", "South East", 0.3, 93108),
    ("Wealden", "South East", 0.205, 160152),
    ("Basildon", "East of England", 0.361, 187571),
    ("Braintree", "East of England", 0.21, 155268),
    ("Brentwood", "East of England", 0.356, 77047),
    ("Castle Point", "East of England", 0.364, 89587),
    ("Chelmsford", "East of England", 0.285, 181523),
    ("Colchester", "East of England", 0.094, 192715),
    ("Epping Forest", "East of England", 0.323, 134980),
    ("Harlow", "East of England", 0.193, 93329),
    ("Maldon", "East of England", 0.086, 66208),
    ("Rochford", "East of England", 0.392, 85661),
    ("Tendring", "East of England", 0.091, 148291),
    ("Uttlesford", "East of England", 0.19, 91341),
    ("Cheltenham", "South West", 0.448, 118836),
    ("Cotswold", "South West", 0.35, 90832),
    ("Forest of Dean", "South West", 0.348, 87004),
    ("Gloucester", "South West", 0.327, 132416),
    ("Stroud", "South West", 0.33, 121104),
    ("Tewkesbury", "South West", 0.428, 94884),
    ("Basingstoke and Deane", "South East", 0.305, 185154),
    ("East Hampshire", "South East", 0.296, 125744),
    ("Eastleigh", "South East", 0.294, 136443),
    ("Fareham", "South East", 0.384, 114511),
    ("Gosport", "South East", 0.316, 81952),
    ("Hart", "South East", 0.218, 99408),
    ("Havant", "South East", 0.447, 124208),
    ("New Forest", "South East", 0.409, 175785),
    ("Rushmoor", "South East", 0.169, 99756),
    ("Test Valley", "South East", 0.376, 130492),
    ("Winchester", "South East", 0.354, 127444),
    ("Broxbourne", "East of England", 0.185, 99009),
    ("Dacorum", "East of England", 0.226, 155081),
    ("Hertsmere", "East of England", 0.208, 107827),
    ("North Hertfordshire", "East of England", 0.298, 133210),
    ("Three Rivers", "East of England", 0.174, 93771),
    ("Watford", "East of England", 0.192, 102246),
    ("Ashford", "South East", 0.35, 132747),
    ("Canterbury", "South East", 0.361, 157432),
    ("Dartford", "South East", 0.233, 116753),
    ("Dover", "South East", 0.301, 116410),
    ("Gravesham", "South East", 0.216, 106900),
    ("Maidstone", "South East", 0.206, 175782),
    ("Sevenoaks", "South East", 0.241, 120514),
    ("Folkestone and Hythe", "South East", 0.27, 109758),
    ("Swale", "South East", 0.281, 151676),
    ("Thanet", "South East", 0.477, 140587),
    ("Tonbridge and Malling", "South East", 0.194, 132201),
    ("Tunbridge Wells", "South East", 0.224, 115311),
    ("Burnley", "North West", 0.476, 94646),
    ("Chorley", "North West", 0.415, 117732),
    ("Fylde", "North West", 0.534, 81374),
    ("Hyndburn", "North West", 0.512, 82234),
    ("Lancaster", "North West", 0.493, 142934),
    ("Pendle", "North West", 0.497, 95757),
    ("Preston", "North West", 0.427, 147835),
    ("Ribble Valley", "North West", 0.482, 61561),
    ("Rossendale", "North West", 0.472, 70871),
    ("South Ribble", "North West", 0.581, 111035),
    ("West Lancashire", "North West", 0.55, 117429),
    ("Wyre", "North West", 0.34, 111946),
    ("Blaby", "East Midlands", 0.417, 102926),
    ("Charnwood", "East Midlands", 0.384, 183971),
    ("Harborough", "East Midlands", 0.403, 97625),
    ("Hinckley and Bosworth", "East Midlands", 0.403, 113642),
    ("Melton", "East Midlands", 0.415, 51752),
    ("North West Leicestershire", "East Midlands", 0.465, 104706),
    ("Oadby and Wigston", "East Midlands", 0.389, 57747),
    ("Boston", "East Midlands", 0.221, 70502),
    ("East Lindsey", "East Midlands", 0.415, 142296),
    ("Lincoln", "East Midlands", 0.451, 103813),
    ("North Kesteven", "East Midlands", 0.338, 118075),
    ("South Holland", "East Midlands", 0.21, 95122),
    ("South Kesteven", "East Midlands", 0.268, 143404),
    ("West Lindsey", "East Midlands", 0.396, 95156),
    ("Breckland", "East of England", 0.298, 141476),
    ("Broadland", "East of England", 0.459, 131721),
    ("Great Yarmouth", "East of England", 0.363, 99748),
    ("King's Lynn and West Norfolk", "East of England", 0.369, 154325),
    ("North Norfolk", "East of England", 0.54, 102980),
    ("Norwich", "East of England", 0.421, 143922),
    ("South Norfolk", "East of England", 0.36, 141948),
    ("Ashfield", "East Midlands", 0.35, 126300),
    ("Bassetlaw", "East Midlands", 0.35, 117804),
    ("Broxtowe", "East Midlands", 0.51, 110940),
    ("Gedling", "East Midlands", 0.309, 117264),
    ("Mansfield", "East Midlands", 0.238, 110482),
    ("Newark and Sherwood", "East Midlands", 0.319, 122956),
    ("Rushcliffe", "East Midlands", 0.404, 119077),
    ("Cherwell", "South East", 0.26, 161016),
    ("Oxford", "South East", 0.103, 162040),
    ("South Oxfordshire", "South East", 0.183, 149085),
    ("Vale of White Horse", "South East", 0.183, 138913),
    ("West Oxfordshire", "South East", 0.201, 114237),
    ("Cannock Chase", "West Midlands", 0.405, 100519),
    ("East Staffordshire", "West Midlands", 0.355, 124020),
    ("Lichfield", "West Midlands", 0.454, 106436),
    ("Newcastle-under-Lyme", "West Midlands", 0.44, 123299),
    ("South Staffordshire", "West Midlands", 0.39, 110472),
    ("Stafford", "West Midlands", 0.356, 136867),
    ("Staffordshire Moorlands", "West Midlands", 0.389, 95845),
    ("Tamworth", "West Midlands", 0.544, 78646),
    ("Babergh", "East of England", 0.244, 92341),
    ("Ipswich", "East of England", 0.225, 139642),
    ("Mid Suffolk", "East of England", 0.298, 102699),
    ("Elmbridge", "South East", 0.159, 138754),
    ("Epsom and Ewell", "South East", 0.235, 80938),
    ("Guildford", "South East", 0.224, 143650),
    ("Mole Valley", "South East", 0.221, 87386),
    ("Reigate and Banstead", "South East", 0.217, 150846),
    ("Runnymede", "South East", 0.158, 88079),
    ("Spelthorne", "South East", 0.162, 102956),
    ("Surrey Heath", "South East", 0.277, 90453),
    ("Tandridge", "South East", 0.222, 87876),
    ("Waverley", "South East", 0.252, 128229),
    ("Woking", "South East", 0.164, 103943),
    ("North Warwickshire", "West Midlands", 0.425, 65035),
    ("Nuneaton and Bedworth", "West Midlands", 0.432, 134197),
    ("Rugby", "West Midlands", 0.318, 114363),
    ("Stratford-on-Avon", "West Midlands", 0.298, 134725),
    ("Warwick", "West Midlands", 0.363, 148453),
    ("Adur", "South East", 0.408, 64544),
    ("Arun", "South East", 0.326, 164889),
    ("Chichester", "South East", 0.3, 124068),
    ("Crawley", "South East", 0.146, 118493),
    ("Horsham", "South East", 0.417, 146778),
    ("Mid Sussex", "South East", 0.291, 152566),
    ("Worthing", "South East", 0.331, 111338),
    ("Bromsgrove", "West Midlands", 0.302, 99183),
    ("Malvern Hills", "West Midlands", 0.353, 79486),
    ("Redditch", "West Midlands", 0.302, 87036),
    ("Worcester", "West Midlands", 0.296, 103872),
    ("Wychavon", "West Midlands", 0.326, 132492),
    ("Wyre Forest", "West Midlands", 0.351, 101607),
    ("St Albans", "East of England", 0.194, 148167),
    ("Welwyn Hatfield", "East of England", 0.159, 119836),
    ("East Hertfordshire", "East of England", 0.143, 150158),
    ("Stevenage", "East of England", 0.381, 89495),
    ("East Suffolk", "East of England", 0.271, 246058),
    ("West Suffolk", "East of England", 0.257, 179948),
    ("Bolton", "North West", 0.474, 295963),
    ("Bury", "North West", 0.49, 193851),
    ("Manchester", "North West", 0.565, 551938),
    ("Oldham", "North West", 0.423, 242088),
    ("Rochdale", "North West", 0.407, 223773),
    ("Salford", "North West", 0.506, 269923),
    ("Stockport", "North West", 0.44, 294773),
    ("Tameside", "North West", 0.435, 231071),
    ("Trafford", "North West", 0.62, 235052),
    ("Wigan", "North West", 0.518, 329330),
    ("Knowsley", "North West", 0.573, 154519),
    ("Liverpool", "North West", 0.66, 486088),
    ("St. Helens", "North West", 0.571, 183248),
    ("Sefton", "North West", 0.56, 279233),
    ("Wirral", "North West", 0.636, 320199),
    ("Barnsley", "Yorkshire and The Humber", 0.436, 244572),
    ("Doncaster", "Yorkshire and The Humber", 0.342, 308106),
    ("Rotherham", "Yorkshire and The Humber", 0.455, 265807),
    ("Sheffield", "Yorkshire and The Humber", 0.374, 556521),
    ("Newcastle upon Tyne", "North East", 0.557, 300125),
    ("North Tyneside", "North East", 0.599, 208967),
    ("South Tyneside", "North East", 0.45, 147776),
    ("Sunderland", "North East", 0.462, 274172),
    ("Birmingham", "West Midlands", 0.429, 1144919),
    ("Coventry", "West Midlands", 0.381, 345325),
    ("Dudley", "West Midlands", 0.384, 323486),
    ("Sandwell", "West Midlands", 0.413, 341832),
    ("Solihull", "West Midlands", 0.37, 216240),
    ("Walsall", "West Midlands", 0.439, 284124),
    ("Wolverhampton", "West Midlands", 0.397, 263727),
    ("Bradford", "Yorkshire and The Humber", 0.457, 546412),
    ("Calderdale", "Yorkshire and The Humber", 0.433, 206631),
    ("Kirklees", "Yorkshire and The Humber", 0.418, 433216),
    ("Leeds", "Yorkshire and The Humber", 0.439, 811956),
    ("Wakefield", "Yorkshire and The Humber", 0.478, 353368),
    ("Gateshead", "North East", 0.522, 196151),
    ("City of London", "London", 0.111, 8583),
    ("Barking and Dagenham", "London", 0.46, 218869),
    ("Barnet", "London", 0.192, 389344),
    ("Bexley", "London", 0.181, 246472),
    ("Brent", "London", 0.116, 339816),
    ("Bromley", "London", 0.275, 329992),
    ("Camden", "London", 0.227, 210136),
    ("Croydon", "London", 0.347, 390719),
    ("Ealing", "London", 0.147, 367115),
    ("Enfield", "London", 0.049, 329984),
    ("Greenwich", "London", 0.291, 289068),
    ("Hackney", "London", 0.241, 259146),
    ("Hammersmith and Fulham", "London", 0.113, 183157),
    ("Haringey", "London", 0.205, 264238),
    ("Harrow", "London", 0.156, 261203),
    ("Havering", "London", 0.464, 262052),
    ("Hillingdon", "London", 0.233, 305909),
    ("Hounslow", "London", 0.073, 288181),
    ("Islington", "London", 0.154, 216589),
    ("Kensington and Chelsea", "London", 0.112, 143375),
    ("Kingston upon Thames", "London", 0.062, 168063),
    ("Lambeth", "London", 0.165, 317654),
    ("Lewisham", "London", 0.356, 300553),
    ("Merton", "London", 0.227, 215186),
    ("Newham", "London", 0.347, 351036),
    ("Redbridge", "London", 0.319, 310260),
    ("Richmond upon Thames", "London", 0.087, 195278),
    ("Southwark", "London", 0.332, 307637),
    ("Sutton", "London", 0.256, 209639),
    ("Tower Hamlets", "London", 0.154, 310306),
    ("Waltham Forest", "London", 0.124, 278426),
    ("Wandsworth", "London", 0.11, 327506),
    ("Westminster", "London", 0.112, 204236),
]

df = pd.DataFrame(councils, columns=["council", "region", "water_stress", "population_k"])
df["population_k"] = df["population_k"].astype(float)
df["water_stress"] = df["water_stress"].astype(float)

# FLIP THE SCORE: Convert Water Availability to a Water Stress Penalty
df["water_stress"] = 1.0 - df["water_stress"]

# ── 2100 SCENARIO MULTIPLIERS ────────────────────────────────────────────
# Stress multipliers applied to PENALTY (post-inversion), capped at 1.0
# Population multipliers applied to raw population figures
tier_stress = {'London': 1.50, 'South East': 1.50, 'East of England': 1.50, 'South West': 1.32, 'North West': 1.15, 'North East': 1.15, 'Yorkshire and The Humber': 1.15, 'West Midlands': 1.15, 'East Midlands': 1.15}
tier_pop = {'London': 1.24, 'South East': 1.24, 'East of England': 1.24, 'South West': 1.26, 'North West': 1.16, 'North East': 1.16, 'Yorkshire and The Humber': 1.16, 'West Midlands': 1.16, 'East Midlands': 1.16}
df['water_stress'] = df.apply(lambda r: min(r['water_stress'] * tier_stress[r['region']], 1.0), axis=1)
df['population_k'] = df.apply(lambda r: float(round(r['population_k'] * tier_pop[r['region']])), axis=1)

df = df.reset_index(drop=True)

print(f"Councils loaded: {len(df)}")
print(df.groupby("region")["council"].count())
print(f"\nTotal population: {df['population_k'].sum():,.0f}k")
print(f"Water stress distribution:\n{df['water_stress'].value_counts().sort_index()}")

# ── 2. PARETO FRONTIER via epsilon-constraint ───────────────────────────────
def solve_dc_placement(df, k, max_stress=None, min_benefit=None, verbose=False):
    """
    Solve: max sum(pop*x) subject to sum(ws*x) <= max_stress, sum(x)=k
    Returns dict with solution or None if infeasible
    """
    n = len(df)
    prob = LpProblem("DataCentres", LpMaximize)
    x = [LpVariable(f"x_{i}", cat='Binary') for i in range(n)]

    # Objective: maximise population
    prob += lpSum(df.loc[i, "population_k"] * x[i] for i in range(n))

    # Exactly k facilities
    prob += lpSum(x[i] for i in range(n)) == k

    # Optional stress cap (epsilon constraint)
    if max_stress is not None:
        prob += lpSum(df.loc[i, "water_stress"] * x[i] for i in range(n)) <= max_stress

    prob.solve(PULP_CBC_CMD(msg=0))

    if LpStatus[prob.status] != "Optimal":
        return None

    selected = [i for i in range(n) if value(x[i]) > 0.5]
    total_pop = sum(df.loc[i, "population_k"] for i in selected)
    total_stress = sum(df.loc[i, "water_stress"] for i in selected)

    return {
        "selected": selected,
        "population_k": round(total_pop, 1),
        "water_stress": round(total_stress, 3),
        "councils": df.loc[selected, "council"].tolist(),
        "regions": df.loc[selected, "region"].tolist(),
    }

# ── 3. SWEEP for k = 6 to 15 ────────────────────────────────────────────────
all_results = {}
pareto_data = []  # flat list for plotting

for k in range(6, 16):
    print(f"\n── k={k} ─────────────")

    # Find bounds: max pop (no stress cap) and min stress (max_stress forced small)
    best = solve_dc_placement(df, k)  # unconstrained max pop
    max_stress_val = best["water_stress"]
    max_pop = best["population_k"]

    # Min stress: flip objective
    prob_min = LpProblem(f"MinStress_k{k}", LpMinimize)
    x = [LpVariable(f"x_{i}", cat='Binary') for i in range(len(df))]
    prob_min += lpSum(df.loc[i, "water_stress"] * x[i] for i in range(len(df)))
    prob_min += lpSum(x[i] for i in range(len(df))) == k
    prob_min.solve(PULP_CBC_CMD(msg=0))
    min_stress = sum(df.loc[i, "water_stress"] * value(x[i]) for i in range(len(df)))
    min_stress = round(min_stress, 3)

    # Sweep epsilon from min_stress to max_stress in ~25 steps
    epsilons = np.linspace(min_stress, max_stress_val, 100)
    frontier = []
    seen = set()

    for eps in epsilons:
        sol = solve_dc_placement(df, k, max_stress=eps)
        if sol is None:
            continue
        key = (sol["population_k"], sol["water_stress"])
        if key in seen:
            continue
        seen.add(key)
        sol["k"] = k
        frontier.append(sol)

    # Keep Pareto-efficient points (max pop for each stress level)
    frontier.sort(key=lambda s: s["water_stress"])
    pareto = []
    best_pop = -1
    for pt in frontier:
        if pt["population_k"] > best_pop:
            best_pop = pt["population_k"]
            pareto.append(pt)

    all_results[k] = pareto
    pareto_data.extend(pareto)
    print(f"  Pareto points: {len(pareto)}  |  Pop range: {pareto[0]['population_k']:.0f}k–{pareto[-1]['population_k']:.0f}k  |  Stress range: {pareto[0]['water_stress']:.2f}–{pareto[-1]['water_stress']:.2f}")

# ── 4. SAVE JSON for downstream use ─────────────────────────────────────────
with open("pareto_results_2100.json", "w") as f:
    json.dump({"councils": df.to_dict(orient="records"), "pareto": pareto_data}, f, indent=2)

print("\n✓ Saved pareto_results.json")
print(f"  Total Pareto solutions: {len(pareto_data)}")
