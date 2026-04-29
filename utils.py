# -*- coding: utf-8 -*-
import math

# =========================================================
# DATA TABLES
# =========================================================

U_ΤΟΙΧΟΥ = {
    "Πριν το 1980, χωρίς μόνωση": 2.20,
    "1980–2000, βασική μόνωση (EPS ~5cm)": 0.80,
    "2000–2010, μέτρια μόνωση (EPS ~8cm)": 0.55,
    "Μετά το 2010, EPS/XPS (ΚΕΝΑΚ)": 0.40,
    "Μετά το 2010, PUR/PIR": 0.28,
    "Ανακαίνιση με εξωτερική μόνωση": 0.35,
}

U_ΟΡΟΦΗΣ_BASE = {
    "Πριν το 1980, χωρίς μόνωση": 1.80,
    "1980–2000, βασική μόνωση (EPS ~5cm)": 0.80,
    "2000–2010, μέτρια μόνωση (EPS ~8cm)": 0.50,
    "Μετά το 2010, EPS/XPS (ΚΕΝΑΚ)": 0.30,
    "Μετά το 2010, PUR/PIR": 0.22,
    "Ανακαίνιση με εξωτερική μόνωση": 0.28,
}

U_ΔΑΠΕΔΟΥ_BASE = {
    "Πριν το 1980, χωρίς μόνωση": 1.20,
    "1980–2000, βασική μόνωση (EPS ~5cm)": 0.70,
    "2000–2010, μέτρια μόνωση (EPS ~8cm)": 0.50,
    "Μετά το 2010, EPS/XPS (ΚΕΝΑΚ)": 0.35,
    "Μετά το 2010, PUR/PIR": 0.28,
    "Ανακαίνιση με εξωτερική μόνωση": 0.32,
}

ΘΕΡΜΟΜΟΝΩΣΗ = {k: v for k, v in zip(U_ΤΟΙΧΟΥ.keys(), [1.30, 1.10, 1.00, 0.90, 0.85, 0.90])}
ΕΤΟΣ = {k: v for k, v in zip(U_ΤΟΙΧΟΥ.keys(), [1.30, 1.12, 1.00, 0.85, 0.80, 0.90])}

ΚΟΥΦΩΜΑΤΑ = {
    "Μονό τζάμι": 5.80,
    "Διπλό αλουμίνιο χωρίς θερμοδιακοπή": 3.20,
    "Διπλό αλουμίνιο με θερμοδιακοπή": 2.20,
    "Διπλό PVC": 1.80,
    "Διπλό low-e": 1.10,
    "Τριπλό low-e": 0.90,
}

ΑΝΟΙΓΜΑΤΑ = {
    "μονή_ανοιγόμενη_μπαλκονόπορτα": 1.89,
    "διπλή_συρόμενη_μπαλκονόπορτα": 3.78,
    "διπλή_ανοιγόμενη_μπαλκονόπορτα": 3.36,
    "μεγάλο_παράθυρο": 1.68,
    "μικρό_παράθυρο": 0.36,
}

ΑΕΡΟΔΙΕΙΣΔΥΣΗ = {"μέτρια": 0.7, "κακή": 1.2, "καλή": 0.4}

# Updated to use "άλλο διαμέρισμα"
ΔΑΠΕΔΟ = ["άλλο διαμέρισμα", "πιλοτή", "μη_θερμαινόμενος_χώρος", "έδαφος"]
ΟΡΟΦΗ = ["ταράτσα_εκτεθειμένη", "κεραμοσκεπή", "μη_θερμαινόμενος_χώρος", "άλλο διαμέρισμα"]

ΤΟΙΧΟΙ = {1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}
ΜΗ_ΘΕΡΜΑΙΝΟΜΕΝΟΙ = {0: 1.0, 1: 1.07, 2: 1.14}
ΗΛΙΑΚΗ_ΕΚΘΕΣΗ = {"πολύ_χαμηλή": 0.22, "χαμηλή": 0.5, "μέση": 1.0, "υψηλή": 1.15, "πολύ_υψηλή": 1.25}

ΕΣΩΤΕΡΙΚΑ = {"υπνοδωμάτιο": 300, "παιδικό_δωμάτιο": 350, "σαλόνι": 500, "σαλοκουζίνα": 1000, "κουζίνα": 700, "γραφείο": 400}
ΕΣΩΤΕΡΙΚΑ_ΣΥΝΤΕΛΕΣΤΗΣ = {k: (0.5 if k == "υπνοδωμάτιο" else 1.0) for k in ΕΣΩΤΕΡΙΚΑ.keys()}

ΝΟΜΟΙ_ΖΩΝΗ = {"Αττική": "Β", "Θεσσαλονίκη": "Γ", "Αργολίδα": "Α", "Γρεβενά": "Δ", "Κρήτη": "Α"} # Truncated list

ΖΩΝΗ_BTU = {"Α": 240, "Β": 210, "Γ": 190, "Δ": 170}
ΖΩΝΗ_ΕΠΟΜΕΝΗ = {"Α": "Β", "Β": "Γ", "Γ": "Δ", "Δ": "Δ"}
COMMERCIAL_SIZES = [7, 9, 10, 12, 13, 14, 16, 18, 20, 22, 24, 30]

# EN 12831 Adjacency b-factors (0.0 for heated apartment contact)
ADJACENCY_B = {
    "άλλο διαμέρισμα": 0.0,
    "μη_θερμαινόμενος_χώρος": 0.50,
    "πιλοτή": 1.0, 
    "ταράτσα_εκτεθειμένη": 1.0,
    "κεραμοσκεπή": 0.90,
    "έδαφος": 0.45,
}

def get_commercial_range(nominal_btu_val):
    val_k = nominal_btu_val / 1000
    suitable_sizes = [s for s in COMMERCIAL_SIZES if s >= val_k]
    if not suitable_sizes: return f"{COMMERCIAL_SIZES[-1]}000+"
    idx = COMMERCIAL_SIZES.index(suitable_sizes[0])
    if idx > 0: return f"{COMMERCIAL_SIZES[idx-1] * 1000:,} – {COMMERCIAL_SIZES[idx] * 1000:,}"
    return f"{COMMERCIAL_SIZES[idx] * 1000:,}"

def compute_kenak_zone(νομός, υψόμετρο_500):
    base = ΝΟΜΟΙ_ΖΩΝΗ.get(νομός, "Β")
    effective = ΖΩΝΗ_ΕΠΟΜΕΝΗ[base] if υψόμετρο_500 and base != "Δ" else base
    return base, effective, ΖΩΝΗ_BTU[effective]

def υπολογισμός(d, mode):
    ΔΤ = abs(d["εξωτερική"] - d["εσωτερική"])
    floor_area = d["επιφάνεια"]
    side = math.sqrt(floor_area)
    total_wall_area = 4 * side * d["ύψος"]
    wall_area = total_wall_area * ΤΟΙΧΟΙ[d["εξωτερικοί"]]
    
    # 1. TRANSMISSION LOSSES
    # Walls
    U_wall = U_ΤΟΙΧΟΥ[d["μόνωση"]]
    
    # Roof logic
    if d["οροφή"] == "άλλο διαμέρισμα":
        U_roof, b_roof = 0, 0
    else:
        U_roof = U_ΟΡΟΦΗΣ_BASE[d["μόνωση_οροφής"]]
        b_roof = ADJACENCY_B.get(d["οροφή"], 1.0)
    
    # Floor logic
    if d["δάπεδο"] == "άλλο διαμέρισμα":
        U_floor, b_floor = 0, 0
    else:
        U_floor = U_ΔΑΠΕΔΟΥ_BASE[d["μόνωση_δάπεδου"]]
        b_floor = ADJACENCY_B.get(d["δάπεδο"], 1.0)

    # Windows
    total_glazing_area = 0
    window_loss = 0
    solar_gain = 0
    windows = [(d["μεγάλα"], "μεγάλο_παράθυρο"), (d["μικρά"], "μικρό_παράθυρο"), 
               (d["μπαλκονόπορτες"], "διπλή_ανοιγόμενη_μπαλκονόπορτα"), 
               (d["μονές"], "μονή_ανοιγόμενη_μπαλκονόπορτα"), (d["συρόμενες"], "διπλή_συρόμενη_μπαλκονόπορτα")]
    
    U_win = ΚΟΥΦΩΜΑΤΑ[d["κουφώματα"]]
    for count, key in windows:
        area = count * ΑΝΟΙΓΜΑΤΑ[key]
        total_glazing_area += area
        window_loss += U_win * area * ΔΤ
        if mode == "ψύξη":
            solar_gain += area * d["βάση_ακτινοβολίας"] * d["ηλιακή_έκθεση"] * 0.35

    eff_wall_area = max(wall_area - total_glazing_area, 0)
    transmission = (U_wall * eff_wall_area * ΔΤ) + (U_roof * floor_area * b_roof * ΔΤ) + \
                   (U_floor * floor_area * b_floor * ΔΤ) + window_loss
    
    # Thermal Bridges
    transmission *= (1.10 if U_wall <= 0.55 else 1.05)

    # 2. INFILTRATION
    volume = floor_area * d["ύψος"]
    base_ach = ΑΕΡΟΔΙΕΙΣΔΥΣΗ[d["αεροστεγανότητα"]]
    leak_amp = 1 + max(0, (ΘΕΡΜΟΜΟΝΩΣΗ[d["μόνωση"]] * ΕΤΟΣ[d["μόνωση"]] - 1.10)) ** 2.2 * 0.8
    infiltration = 0.33 * base_ach * leak_amp * volume * ΔΤ

    # 3. TOTALS
    internal = 0
    breakdown_solar = 0
    if mode == "θέρμανση":
        total = (transmission + infiltration) * 1.10 
        if d.get("βόρειος"): total *= 1.15
    else:
        roof_solar_coeff = {"ταράτσα_εκτεθειμένη": 35, "κεραμοσκεπή": 22, "μη_θερμαινόμενος_χώρος": 10}.get(d["οροφή"], 0)
        roof_solar = floor_area * roof_solar_coeff * d["ηλιακή_έκθεση"]
        internal = ΕΣΩΤΕΡΙΚΑ[d["τύπος"]] * ΕΣΩΤΕΡΙΚΑ_ΣΥΝΤΕΛΕΣΤΗΣ[d["τύπος"]]
        total = transmission + infiltration + solar_gain + roof_solar + internal
        breakdown_solar = solar_gain + roof_solar

    # 4. DERATING
    temp = d["εξωτερική"]
    f_derating = 1.0 
    if mode == "θέρμανση":
        if temp < 0: f_derating = 0.75
        elif temp < 7: f_derating = 0.92
    else:
        if temp > 40: f_derating = 0.90
        elif temp > 35: f_derating = 0.97

    load_btu = total * 3.412
    nominal_btu_base = load_btu / f_derating
    nominal_btu_final = nominal_btu_base
    penalties = {}
    if d.get("περιστασιακή"):
        nominal_btu_final *= 1.25
        penalties["Περιστασιακή"] = 1.25
    if d.get("αθόρυβη"):
        nominal_btu_final *= 1.20
        penalties["Αθόρυβη"] = 1.20

    breakdown = {
        "Τοίχοι": U_wall * eff_wall_area * ΔΤ,
        "Οροφή": U_roof * floor_area * b_roof * ΔΤ,
        "Δάπεδο": U_floor * floor_area * b_floor * ΔΤ,
        "Ανοίγματα": window_loss,
        "Αερισμός": infiltration,
        "Ηλιακά/Εσωτερικά": breakdown_solar + (internal if mode=="ψύξη" else 0)
    }

    return total/1000, load_btu, nominal_btu_base, nominal_btu_final, penalties, breakdown, f_derating
