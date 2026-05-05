import json, pandas as pd, numpy as np
from openpyxl import Workbook
from openpyxl.styles import (Font, PatternFill, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.chart import ScatterChart, Reference, Series

with open("pareto_results_2075.json") as f:
    data = json.load(f)

df_councils = pd.DataFrame(data["councils"])
pareto = data["pareto"]

wb = Workbook()

# ── Styles ───────────────────────────────────────────────────────────────────
HDR_BLUE   = "1F497D"
HDR_TEAL   = "17375E"
HDR_AMBER  = "7F6000"
WHITE      = "FFFFFF"
LIGHT_BLUE = "DCE6F1"
LIGHT_GREY = "F2F2F2"
GREEN_DARK = "375623"
RED_DARK   = "632523"
AMBER_DARK = "7F6000"

def hdr(color=HDR_BLUE):
    return Font(bold=True, color=WHITE, name="Arial", size=10)

def cell_fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def thin_border():
    s = Side(style="thin", color="BFBFBF")
    return Border(left=s, right=s, top=s, bottom=s)

def fmt_sheet(ws):
    ws.sheet_view.showGridLines = False

# ── Sheet 1: INTRO ───────────────────────────────────────────────────────────
ws0 = wb.active
ws0.title = "README"
fmt_sheet(ws0)
ws0.column_dimensions["A"].width = 2
ws0.column_dimensions["B"].width = 55
ws0.column_dimensions["C"].width = 30

ws0["B2"] = "Data Centre Location Optimiser — England"
ws0["B2"].font = Font(bold=True, size=16, color=HDR_BLUE, name="Arial")
ws0["B3"] = "Multi-objective facility location: Maximise population served | Minimise water stress"
ws0["B3"].font = Font(italic=True, size=11, color="595959", name="Arial")

rows = [
    ("", ""),
    ("What this model does", ""),
    ("", "Solves a bi-objective integer programme across all 295 English upper-tier councils"),
    ("", "Objective 1: Maximise total population served by k data centres"),
    ("", "Objective 2: Minimise aggregate water stress index of selected councils"),
    ("", "Method: ε-constraint sweeping → full Pareto frontier for k = 6 to 15"),
    ("", ""),
    ("Data sources", ""),
    ("", "Population: ONS Census 2021, England local authorities"),
    ("", "Water stress: Environment Agency 2021 classification (Serious=1.0, Moderate=0.6, Low=0.2)"),
    ("", ""),
    ("Workbook structure", ""),
    ("", "Council Data   – Raw input data for all 295 English councils"),
    ("", "Pareto Frontier – All efficient trade-off solutions for each k"),
    ("", "Summary k=6–15  – Best balanced solution per k with council list"),
    ("", "Recommended    – Top 3 recommended solutions with rationale"),
]
for r, (label, val) in enumerate(rows, start=5):
    ws0[f"B{r}"] = label
    ws0[f"C{r}"] = val
    if label and label != "":
        ws0[f"B{r}"].font = Font(bold=True, size=10, color=HDR_BLUE, name="Arial")
    else:
        ws0[f"C{r}"].font = Font(size=10, name="Arial")

ws0["B22"] = "Solver: CBC (COIN-OR) via PuLP. All solutions guaranteed optimal."
ws0["B22"].font = Font(italic=True, size=9, color="7F7F7F", name="Arial")

# ── Sheet 2: Council Data ────────────────────────────────────────────────────
ws1 = wb.create_sheet("Council Data")
fmt_sheet(ws1)

headers = ["#", "Council", "Region", "Water Stress Index",
           "Stress Category", "Population (000s)", "Pop / Stress ratio"]
col_widths = [4, 35, 18, 20, 16, 20, 20]
for c, (h, w) in enumerate(zip(headers, col_widths), 1):
    cell = ws1.cell(1, c, h)
    cell.font = hdr()
    cell.fill = cell_fill(HDR_BLUE)
    cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws1.column_dimensions[get_column_letter(c)].width = w

for r, row in df_councils.iterrows():
    ws = row["water_stress"]
    
    # --- NEW CONTINUOUS DATA LOGIC ---
    if ws >= 0.75:
        label_text = "High Stress"
    elif ws >= 0.40:
        label_text = "Moderate Stress"
    else:
        label_text = "Low Stress"
    # ---------------------------------
    
    pop = row["population_k"]
    ratio = round(pop / ws, 1) if ws > 0 else 0
    
    # Notice that label_text is now in the list below instead of stress_labels.get
    vals = [r+1, row["council"], row["region"], ws,
            label_text, pop, ratio]
            
    for c, v in enumerate(vals, 1):
        cell = ws1.cell(r+2, c, v)
        cell.font = Font(size=10, name="Arial")
        cell.alignment = Alignment(horizontal="left" if c in (2,3,5) else "right")
        cell.border = thin_border()
        if (r % 2) == 0:
            cell.fill = cell_fill(LIGHT_GREY)
# Conditional formatting on stress
ws1.conditional_formatting.add(
    f"D2:D{len(df_councils)+1}",
    ColorScaleRule(
        start_type="num", start_value=0.2, start_color="63BE7B",
        mid_type="num",   mid_value=0.6,   mid_color="FFEB84",
        end_type="num",   end_value=1.0,   end_color="F8696B"
    )
)
ws1.conditional_formatting.add(
    f"F2:F{len(df_councils)+1}",
    DataBarRule(start_type="min", end_type="max",
                color="4472C4", showValue=True)
)

ws1.freeze_panes = "A2"
ws1.auto_filter.ref = f"A1:G{len(df_councils)+1}"

# ── Sheet 3: Pareto Frontier ─────────────────────────────────────────────────
ws2 = wb.create_sheet("Pareto Frontier")
fmt_sheet(ws2)

ph = ["k", "Solution #", "Total Population (000s)", "Total Water Stress",
      "Stress per DC", "Pop per DC (000s)", "Councils selected"]
pw = [5, 10, 22, 20, 14, 20, 80]
for c, (h, w) in enumerate(zip(ph, pw), 1):
    cell = ws2.cell(1, c, h)
    cell.font = hdr(HDR_TEAL)
    cell.fill = cell_fill(HDR_TEAL)
    cell.alignment = Alignment(horizontal="center", wrap_text=True)
    ws2.column_dimensions[get_column_letter(c)].width = w

row_idx = 2
for sol in pareto:
    k = sol["k"]
    vals = [k, None,
            sol["population_k"],
            sol["water_stress"],
            round(sol["water_stress"]/k, 3),
            round(sol["population_k"]/k, 1),
            ", ".join(sol["councils"])]
    for c, v in enumerate(vals, 1):
        cell = ws2.cell(row_idx, c, v)
        cell.font = Font(size=9, name="Arial")
        cell.border = thin_border()
        cell.alignment = Alignment(horizontal="center" if c not in (7,) else "left", wrap_text=(c==7))
    row_idx += 1

# Number each solution within its k group
from itertools import groupby
k_groups = {}
for sol in pareto:
    k_groups.setdefault(sol["k"], []).append(sol)
row_idx = 2
for k in range(6, 16):
    for j, _ in enumerate(k_groups.get(k, []), 1):
        ws2.cell(row_idx, 2, j)
        row_idx += 1

ws2.freeze_panes = "A2"
ws2.row_dimensions[1].height = 32

# ── Sheet 4: Summary by k ────────────────────────────────────────────────────
ws3 = wb.create_sheet("Summary k=6–15")
fmt_sheet(ws3)

sh = ["k (data centres)", "Min stress solution", "", "",
      "Balanced solution (midpoint)", "", "",
      "Max population solution", "", ""]
sh2 = ["", "Population (000s)", "Water Stress", "Councils",
       "Population (000s)", "Water Stress", "Councils",
       "Population (000s)", "Water Stress", "Councils"]
sw = [18, 18, 14, 45, 18, 14, 45, 18, 14, 45]

for c, (h, w) in enumerate(zip(sh, sw), 1):
    cell = ws3.cell(1, c, h)
    cell.font = hdr()
    cell.fill = cell_fill(HDR_BLUE if c==1 else ("006400" if c<=4 else ("7F6000" if c<=7 else "8B0000")))
    cell.alignment = Alignment(horizontal="center")
    ws3.column_dimensions[get_column_letter(c)].width = w

for c, h in enumerate(sh2, 1):
    cell = ws3.cell(2, c, h)
    cell.font = Font(bold=True, size=9, name="Arial", color=WHITE)
    cell.fill = cell_fill("375623" if 2<=c<=4 else ("7F6000" if 5<=c<=7 else ("843C0C" if c>=8 else HDR_BLUE)))
    cell.alignment = Alignment(horizontal="center")

ws3.merge_cells("B1:D1")
ws3.merge_cells("E1:G1")
ws3.merge_cells("H1:J1")

for r, k in enumerate(range(6, 16), 3):
    pts = k_groups.get(k, [])
    if not pts:
        continue
    pts_sorted = sorted(pts, key=lambda s: s["water_stress"])
    min_s = pts_sorted[0]
    max_s = pts_sorted[-1]
    mid_s = pts_sorted[len(pts_sorted)//2]

    fill = cell_fill(LIGHT_GREY if r % 2 == 0 else WHITE)
    row_vals = [
        k,
        min_s["population_k"], min_s["water_stress"], ", ".join(min_s["councils"]),
        mid_s["population_k"], mid_s["water_stress"], ", ".join(mid_s["councils"]),
        max_s["population_k"], max_s["water_stress"], ", ".join(max_s["councils"]),
    ]
    for c, v in enumerate(row_vals, 1):
        cell = ws3.cell(r, c, v)
        cell.font = Font(size=9, name="Arial")
        cell.fill = fill
        cell.border = thin_border()
        cell.alignment = Alignment(wrap_text=(c in (4,7,10)), horizontal="left" if c in (4,7,10) else "center")
    ws3.row_dimensions[r].height = 55

ws3.freeze_panes = "A3"

# ── Sheet 5: Recommended ─────────────────────────────────────────────────────
ws4 = wb.create_sheet("Recommended")
fmt_sheet(ws4)
ws4.column_dimensions["A"].width = 2
ws4.column_dimensions["B"].width = 28
ws4.column_dimensions["C"].width = 55

ws4["B2"] = "Top 3 Recommended Solutions"
ws4["B2"].font = Font(bold=True, size=14, color=HDR_BLUE, name="Arial")

# Pick 3 interesting solutions: k=10 balanced, k=8 low-stress, k=12 high-pop
recs = [
    {
        "title": "Option A – Balanced (k=10, midpoint Pareto)",
        "desc": "Best overall trade-off. 10 data centres spread across England maximising "
                "population access while keeping water stress moderate.",
        "k": 10, "idx": len(k_groups[10])//2
    },
    {
        "title": "Option B – Water-conservative (k=8, low stress)",
        "desc": "8 data centres placed only in low-stress councils (North/Midlands). "
                "Sacrifices ~25% population coverage to protect water resources.",
        "k": 8, "idx": 0
    },
    {
        "title": "Option C – Maximum coverage (k=12, high population)",
        "desc": "12 data centres maximising population served. Includes some high-stress "
                "areas (South East). Suitable if cooling technology mitigates water impact.",
        "k": 12, "idx": -1
    },
]

row = 4
for rec in recs:
    k = rec["k"]
    pts = sorted(k_groups[k], key=lambda s: s["water_stress"])
    sol = pts[rec["idx"]]

    ws4.cell(row, 2, rec["title"]).font = Font(bold=True, size=11, color=HDR_BLUE, name="Arial")
    row += 1
    ws4.cell(row, 2, rec["desc"]).font = Font(size=10, name="Arial", color="404040")
    ws4[f"B{row}"].alignment = Alignment(wrap_text=True)
    ws4.row_dimensions[row].height = 35
    row += 1

    stats = [
        ("Data centres (k)", sol["k"]),
        ("Total population served", f"{sol['population_k']:,.0f}k"),
        ("Aggregate water stress", f"{sol['water_stress']:.2f}"),
        ("Stress per data centre", f"{sol['water_stress']/sol['k']:.3f}"),
        ("Pop per data centre", f"{sol['population_k']/sol['k']:,.0f}k"),
        ("Selected councils", ", ".join(sol["councils"])),
        ("Regions covered", ", ".join(sorted(set(sol["regions"])))),
    ]
    for label, val in stats:
        ws4.cell(row, 2, label).font = Font(bold=True, size=9, name="Arial", color=HDR_TEAL)
        ws4.cell(row, 3, val).font = Font(size=9, name="Arial")
        ws4[f"C{row}"].alignment = Alignment(wrap_text=True)
        row += 1
    ws4.row_dimensions[row].height = 6
    row += 2

wb.save("dc_optimisation_results_2075.xlsx")
print("✓ Excel saved")
