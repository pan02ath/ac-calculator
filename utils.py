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
    "Διπλό αλουμίνιο χωρίς θερμοδιακοπή": 3.20,
    "Διπλό αλουμίνιο με θερμοδιακοπή": 2.20,
    "Διπλό PVC": 1.80,
    "Διπλό low-e": 1.10,
    "Τριπλό low-e": 0.90,
    "Μονό τζάμι": 5.80,
}

ΑΝΟΙΓΜΑΤΑ = {
    "μονή_ανοιγόμενη_μπαλκονόπορτα": 1.89,
    "διπλή_συρόμενη_μπαλκονόπορτα": 3.78,
    "διπλή_ανοιγόμενη_μπαλκονόπορτα": 3.36,
    "μεγάλο_παράθυρο": 1.68,
    "μικρό_παράθυρο": 0.36,
}

ΑΕΡΟΔΙΕΙΣΔΥΣΗ = {"μέτρια": 1.0, "κακή": 1.8, "καλή": 0.4}

ΔΑΠΕΔΟ = ["άλλο διαμέρισμα", "πιλοτή", "μη_θερμαινόμενος_χώρος", "έδαφος"]
ΟΡΟΦΗ = ["άλλο διαμέρισμα", "ταράτσα_εκτεθειμένη", "κεραμοσκεπή", "μη_θερμαινόμενος_χώρος"]

ΤΟΙΧΟΙ = {1: 0.25, 2: 0.50, 3: 0.75, 4: 1.0}
ΜΗ_ΘΕΡΜΑΙΝΟΜΕΝΟΙ = {0: 1.0, 1: 1.07, 2: 1.14}
ΗΛΙΑΚΗ_ΕΚΘΕΣΗ = {"μέση": 1.0, "υψηλή": 1.15, "πολύ_υψηλή": 1.25, "χαμηλή": 0.5, "πολύ_χαμηλή": 0.22}

ΕΣΩΤΕΡΙΚΑ = {"υπνοδωμάτιο": 300, "παιδικό_δωμάτιο": 350, "σαλόνι": 500, "σαλοκουζίνα": 1000, "κουζίνα": 700, "γραφείο": 400}
ΕΣΩΤΕΡΙΚΑ_ΣΥΝΤΕΛΕΣΤΗΣ = {k: (0.5 if k == "υπνοδωμάτιο" else 1.0) for k in ΕΣΩΤΕΡΙΚΑ.keys()}

ΝΟΜΟΙ_ΖΩΝΗ = {
    "Αττική":              "Β",  
    "Θεσσαλονίκη":         "Γ",  
    "Αιτωλοακαρνανία":     "Β",
    "Αργολίδα":            "Α",
    "Αρκαδία":             "Β",
    "Άρτα":                "Β",
    "Αχαΐα":               "Β",
    "Βοιωτία":             "Β",
    "Γρεβενά":             "Δ",
    "Δράμα":               "Δ",
    "Δωδεκάνησα":          "Α",
    "Έβρος":               "Γ",
    "Εύβοια":              "Β",
    "Ευρυτανία":           "Γ",
    "Ζάκυνθος":            "Α",
    "Ηλεία":               "Β",
    "Ημαθία":              "Γ",
    "Θεσπρωτία":           "Β",
    "Ιθάκη":               "Α",
    "Ιωάννινα":            "Γ",
    "Καβάλα":              "Γ",
    "Καρδίτσα":            "Γ",
    "Καστοριά":            "Δ",
    "Κέρκυρα":             "Β",
    "Κεφαλλονιά":          "Α",
    "Κιλκίς":              "Γ",
    "Κοζάνη":              "Δ",
    "Κορινθία":            "Β",
    "Κρήτη":               "Α",
    "Κύθηρα":              "Α",
    "Κυκλάδες":            "Α",
    "Λακωνία":             "Α",
    "Λάρισα":              "Γ",
    "Λέσβος":              "Β",
    "Λευκάδα":             "Β",
    "Μαγνησία":            "Β",
    "Μεσσηνία":            "Α",
    "Ξάνθη":               "Γ",
    "Πέλλα":               "Γ",
    "Πιερία":              "Γ",
    "Πρέβεζα":             "Β",
    "Ροδόπη":              "Γ",
    "Σέρρες":              "Γ",
    "Τρίκαλα":             "Γ",
    "Ύδρα/Σπέτσες/Πόρος":  "Α",
    "Φθιώτιδα":            "Β",
    "Φλώρινα":             "Δ",
    "Φωκίδα":              "Β",
    "Χαλκιδική":           "Γ",
    "Χίος":                "Β",
}

ΖΩΝΗ_BTU = {"Α": 240, "Β": 210, "Γ": 190, "Δ": 170}
ΖΩΝΗ_ΕΠΟΜΕΝΗ = {"Α": "Β", "Β": "Γ", "Γ": "Δ", "Δ": "Δ"}
COMMERCIAL_SIZES = [7, 9, 10, 12, 13, 14, 16, 18, 20, 22, 24, 30]

# EN 12831 Adjacency b-factors
ADJACENCY_B = {
    "άλλο διαμέρισμα": 0.1,         # Neighbor assumed heated
    "μη_θερμαινόμενος_χώρος": 0.50, # Standard EN value
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
    
    # Deriving geometry
    side_length = math.sqrt(floor_area)
    wall_height = d["ύψος"]
    single_wall_gross_area = side_length * wall_height
    
    # 1. TRANSMISSION LOSSES
    total_ext_wall_area = 4 * single_wall_gross_area * ΤΟΙΧΟΙ[d["εξωτερικοί"]]
    
    total_glazing_area = (
        d["μεγάλα"] * ΑΝΟΙΓΜΑΤΑ["μεγάλο_παράθυρο"] +
        d["μικρά"] * ΑΝΟΙΓΜΑΤΑ["μικρό_παράθυρο"] +
        d["μπαλκονόπορτες"] * ΑΝΟΙΓΜΑΤΑ["διπλή_ανοιγόμενη_μπαλκονόπορτα"] +
        d["μονές"] * ΑΝΟΙΓΜΑΤΑ["μονή_ανοιγόμενη_μπαλκονόπορτα"] +
        d["συρόμενες"] * ΑΝΟΙΓΜΑΤΑ["διπλή_συρόμενη_μπαλκονόπορτα"]
    )
    U_win = ΚΟΥΦΩΜΑΤΑ[d["κουφώματα"]]
    window_loss = U_win * total_glazing_area * ΔΤ
    
    eff_ext_wall_area = max(total_ext_wall_area - total_glazing_area, 0)
    U_wall = U_ΤΟΙΧΟΥ[d["μόνωση"]]
    ext_wall_loss = U_wall * eff_ext_wall_area * ΔΤ

    U_int_wall = 2.0 if d["μόνωση"] == "Πριν το 1980, χωρίς μόνωση" else 0.70
    unheated_wall_loss = d["μη_θερμαινόμενοι"] * single_wall_gross_area * U_int_wall * 0.50 * ΔΤ

    # D. ROOF & FLOOR
    b_roof = ADJACENCY_B.get(d["οροφή"], 1.0)
    b_floor = ADJACENCY_B.get(d["δάπεδο"], 1.0)
    U_roof = U_ΟΡΟΦΗΣ_BASE.get(d["μόνωση_οροφής"], 2.0)
    U_floor = U_ΔΑΠΕΔΟΥ_BASE.get(d["μόνωση_δάπεδου"], 2.0)

    roof_loss  = U_roof  * floor_area * b_roof  * ΔΤ
    floor_loss = U_floor * floor_area * b_floor * ΔΤ

    # 2. TOTAL TRANSMISSION & BRIDGES
    transmission = (ext_wall_loss + unheated_wall_loss + roof_loss + floor_loss + window_loss)
    # EN ISO 14683 simplified correction
    # Maps to ΔUwb: 0.15 (no insulation), 0.10 (standard), 0.05 (well insulated)
    if U_wall >= 1.50:      # Pre-1980, uninsulated
        thermal_bridges = 1.15
    elif U_wall >= 0.45:    # 1980–2010, basic/medium
        thermal_bridges = 1.10
    else:                   # Post-2010, KENAK/PUR
        thermal_bridges = 1.05    
    transmission *= thermal_bridges

    # 3. INFILTRATION
    volume = floor_area * wall_height
    base_ach = ΑΕΡΟΔΙΕΙΣΔΥΣΗ[d["αεροστεγανότητα"]]
    infiltration = 0.33 * base_ach * volume * ΔΤ

    # 4. TOTALS
    solar_gain = 0
    internal = 0
    if mode == "ψύξη":
        solar_gain = total_glazing_area * d["βάση_ακτινοβολίας"] * d["ηλιακή_έκθεση"] * 0.35
        internal = ΕΣΩΤΕΡΙΚΑ[d["τύπος"]] * ΕΣΩΤΕΡΙΚΑ_ΣΥΝΤΕΛΕΣΤΗΣ[d["τύπος"]]
        total = transmission + infiltration + solar_gain + internal
    else:
        total = (transmission + infiltration) * 1.10 
        if d.get("βόρειος"): total *= 1.15

    # 5. SOPHISTICATED DERATING (Performance Adjustment)
    # Replaces the old f_derating with a smart 3-stage model
    f_performance = 1.0
    ext_temp = d["εξωτερική"]

    if mode == "θέρμανση":
        if ext_temp >= 7:
            f_performance = 1.0
        elif 4 <= ext_temp < 7:
            # Gentle decline
            f_performance = 1.0 - (0.015 * (7 - ext_temp))
        elif -2 <= ext_temp < 4:
            # SHARP DECLINE (Defrost Zone: 4°C to -2°C)
            # Loss of approx 5% base + 4.5% per degree
            drop = 0.05 + (0.045 * (4 - ext_temp)) 
            f_performance = 1.0 - drop
        else:
            # STABILIZED COLD (Below -2°C)
            # Starts from the ~0.70 base with a slower 1% per degree decline
            f_performance = 0.70 - (0.01 * (-2 - ext_temp))
    else:
        # Cooling derating (above 35°C)
        if ext_temp > 35:
            f_performance = 1.0 - (0.015 * (ext_temp - 35))

    # Safety minimum to prevent division by zero or negative results
    f_performance = max(f_performance, 0.45)
    
    load_btu = total * 3.412
    nominal_btu_base = load_btu / f_performance # This calculates the required 'labeled' size
    
    # 6. USAGE PENALTIES
    nominal_btu_final = nominal_btu_base
    penalties = {}
    if d.get("περιστασιακή"):
        nominal_btu_final *= 1.25
        penalties["Περιστασιακή χρήση"] = 1.25
    if d.get("αθόρυβη"):
        nominal_btu_final *= 1.20
        penalties["Αθόρυβη/χαμηλή ταχύτητα"] = 1.20

    breakdown = {
        "Εξωτερικοί Τοίχοι": ext_wall_loss,
        "Τοίχοι (Μη θερμαινόμενοι)": unheated_wall_loss,
        "Οροφή": roof_loss,
        "Δάπεδο": floor_loss,
        "Ανοίγματα": window_loss,
        "Αερισμός": infiltration,
        "Ηλιακά/Εσωτερικά": solar_gain + internal
    }

    # IMPORTANT: Ensure f_performance is returned as the last value to match your UI requirements
    return total/1000, load_btu, nominal_btu_base, nominal_btu_final, penalties, breakdown, f_performance
