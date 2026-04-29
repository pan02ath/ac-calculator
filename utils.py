# =========================================================
# ENGINE
# =========================================================
def υπολογισμός(d, mode):
    volume = d["επιφάνεια"] * d["ύψος"]
    ΔΤ = abs(d["εξωτερική"] - d["εσωτερική"])
    floor_area = max(d["επιφάνεια"], 1)
    side = math.sqrt(floor_area)
    total_wall_area = 2 * d["ύψος"] * side * 2
    wall_area = total_wall_area * ΤΟΙΧΟΙ[d["εξωτερικοί"]]
    roof_area = floor_area if d["οροφή_υπάρχει"] else 0

    U_wall  = U_ΤΟΙΧΟΥ[d["μόνωση"]]
    U_roof  = 0.35 * ΟΡΟΦΗ.get(d["οροφή"], 1.0) if d["οροφή_υπάρχει"] else 0
    U_floor = 0.60 * ΔΑΠΕΔΟ[d["δάπεδο"]]
    U_win   = ΚΟΥΦΩΜΑΤΑ[d["κουφώματα"]]

    b_roof  = ADJACENCY_B.get(d["οροφή"], 1.0) if d["οροφή_υπάρχει"] else 0
    b_floor = ADJACENCY_B.get(d["δάπεδο"], 1.0)

    window_loss = 0
    solar_gain = 0
    total_glazing_area = 0
    windows = [
        (d["μεγάλα"],         "μεγάλο_παράθυρο"),
        (d["μικρά"],          "μικρό_παράθυρο"),
        (d["μπαλκονόπορτες"], "διπλή_ανοιγόμενη_μπαλκονόπορτα"),
        (d["μονές"],          "μονή_ανοιγόμενη_μπαλκονόπορτα"),
        (d["συρόμενες"],      "διπλή_συρόμενη_μπαλκονόπορτα"),
    ]
    for count, key in windows:
        area = count * ΑΝΟΙΓΜΑΤΑ[key]
        total_glazing_area += area
        window_loss += U_win * area * ΔΤ
        if mode == "ψύξη":
            solar_gain += area * d["βάση_ακτινοβολίας"] * d["ηλιακή_έκθεση"] * 0.35

    roof_solar = 0
    if mode == "ψύξη" and d["οροφή_υπάρχει"]:
        coeffs = {
            "ταράτσα_εκτεθειμένη": 35,
            "μονωμένη": 15,
            "κεραμοσκεπή": 22,
            "θερμαινόμενος_χώρος": 0,
        }
        roof_solar = roof_area * coeffs.get(d["οροφή"], 0) * d["ηλιακή_έκθεση"]

    effective_wall_area = max(wall_area - total_glazing_area, 0)
    internal = ΕΣΩΤΕΡΙΚΑ[d["τύπος"]] * ΕΣΩΤΕΡΙΚΑ_ΣΥΝΤΕΛΕΣΤΗΣ[d["τύπος"]]

    transmission = (
        U_wall  * effective_wall_area * ΔΤ
        + U_roof  * roof_area * b_roof * ΔΤ
        + U_floor * floor_area * b_floor * ΔΤ
        + window_loss
    )

    insulated = U_wall <= 0.55
    thermal_bridge_penalty = 0.10 if insulated else 0.05
    transmission *= (1 + thermal_bridge_penalty)

    base_ach = ΑΕΡΟΔΙΕΙΣΔΥΣΗ[d["αεροστεγανότητα"]]

    insulation_severity = ΘΕΡΜΟΜΟΝΩΣΗ[d["μόνωση"]]
    age_severity = ΕΤΟΣ[d["έτος"]]
    envelope_weakness = insulation_severity * age_severity
    leakage_amplification = 1 + max(0, (envelope_weakness - 1.10)) ** 2.2 * 0.8
    ACH_effective = base_ach * leakage_amplification

    infiltration = 0.33 * ACH_effective * volume * ΔΤ

    if mode == "θέρμανση":
        total = (transmission + infiltration) * 1.10
        north_penalty_watts = total * 0.15 if d.get("βόρειος") else 0
        total += north_penalty_watts
    else:
        total = transmission + infiltration + solar_gain + roof_solar + internal
        north_penalty_watts = 0
        if "Ζώνη Α" in d["kenak_label"]:
            total *= 1.07
        elif "Ζώνη Β" in d["kenak_label"]:
            total *= 1.04

    total = max(total, 0)
    load_btu = total * 3.412

    temp = d["εξωτερική"]
    if mode == "θέρμανση":
        if temp >= 7:          f_derating = 1.00
        elif 4 <= temp < 7:    f_derating = 0.96
        elif 0 <= temp < 4:    f_derating = 0.88
        elif -7 <= temp < 0:   f_derating = 0.75
        else:                  f_derating = 0.65
    else:
        if temp <= 35:         f_derating = 1.00
        elif temp <= 40:       f_derating = 0.97
        else:                  f_derating = 0.90

    nominal_btu_base = load_btu / f_derating
    nominal_btu_final = nominal_btu_base
    unit_penalty_factors = {}

    if d.get("περιστασιακή"):
        factor = 1.25
        nominal_btu_final *= factor
        unit_penalty_factors["Περιστασιακή χρήση"] = factor

    if d.get("αθόρυβη"):
        nominal_btu_final *= 1.20
        unit_penalty_factors["Αθόρυβη/χαμηλή ταχύτητα"] = 1.20

    breakdown = {
        "Τοίχοι":                  U_wall * effective_wall_area * ΔΤ * (1 + thermal_bridge_penalty),
        "Οροφή":                   U_roof * roof_area * b_roof * ΔΤ,
        "Δάπεδο":                  U_floor * floor_area * b_floor * ΔΤ,
        "Ανοίγματα":               U_win * total_glazing_area * ΔΤ,
        "Αεροδιείσδυση":           infiltration,
        "Ήλιος":                   (solar_gain + roof_solar) if mode == "ψύξη" else 0,
        "Εσωτερικά φορτία":        internal if mode == "ψύξη" else 0,
        "Βόρειος προσανατολισμός": north_penalty_watts if mode == "θέρμανση" else 0,
    }

    return total / 1000, load_btu, nominal_btu_base, nominal_btu_final, unit_penalty_factors, breakdown, f_derating
