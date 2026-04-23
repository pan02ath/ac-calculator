def υπολογισμός(d, mode):

    # =========================================================
    # BASIC GEOMETRY
    # =========================================================
    volume = d["επιφάνεια"] * d["ύψος"]
    ΔΤ = abs(d["εξωτερική"] - d["εσωτερική"])

    floor_area = d["επιφάνεια"]
    height = d["ύψος"]

    # Approximate wall area (assuming rectangular space)
    wall_area = 2 * height * (floor_area ** 0.5) * 2  # simplified perimeter
    roof_area = floor_area if d["οροφή_υπάρχει"] else 0

    # =========================================================
    # U-VALUES (SIMPLIFIED DEFAULTS)
    # =========================================================
    U_wall_base = 1.5
    U_roof_base = 1.2
    U_floor_base = 1.3

    # Apply insulation + year improvement
    U_wall = U_wall_base * ΘΕΡΜΟΜΟΝΩΣΗ[d["μόνωση"]] * ΕΤΟΣ[d["έτος"]]
    U_roof = U_roof_base * (ΟΡΟΦΗ[d["οροφή"]] if d["οροφή_υπάρχει"] else 1.0)
    U_floor = U_floor_base * ΔΑΠΕΔΟ[d["δάπεδο"]]

    # Adjust for exposure
    U_wall *= ΤΟΙΧΟΙ[d["εξωτερικοί"]]
    U_wall *= ΜΗ_ΘΕΡΜΑΙΝΟΜΕΝΟΙ[d["μη_θερμαινόμενοι"]]

    # =========================================================
    # WINDOW CALCULATIONS
    # =========================================================
    glazing_factor = ΚΟΥΦΩΜΑΤΑ[d["κουφώματα"]]

    window_area = 0
    window_loss = 0
    solar_gain = 0

    for k, key in [
        ("μεγάλα", "μεγάλο_παράθυρο"),
        ("μικρά", "μικρό_παράθυρο"),
        ("μπαλκονόπορτες", "διπλή_ανοιγόμενη_μπαλκονόπορτα"),
        ("μονές", "μονή_ανοιγόμενη_μπαλκονόπορτα"),
        ("συρόμενες", "διπλή_συρόμενη_μπαλκονόπορτα")
    ]:
        count = d[k]
        area = count * ΑΝΟΙΓΜΑΤΑ[key]

        window_area += area

        U_window = U_ΑΝΟΙΓΜΑΤΩΝ[key] * glazing_factor
        window_loss += U_window * area * ΔΤ

        # Simplified solar model
        irradiance = 180 * d["ήλιος"]  # W/m² simplified
        SHGC = 0.6 * glazing_factor    # crude solar coefficient
        solar_gain += area * irradiance * SHGC

    # =========================================================
    # TRANSMISSION LOSSES
    # =========================================================
    Q_walls = U_wall * wall_area * ΔΤ
    Q_roof = U_roof * roof_area * ΔΤ
    Q_floor = U_floor * floor_area * ΔΤ

    transmission = Q_walls + Q_roof + Q_floor + window_loss

    # =========================================================
    # INFILTRATION (ACH-BASED)
    # =========================================================
    ach_map = {
        "κακή": 1.2,
        "μέτρια": 0.7,
        "καλή": 0.4
    }

    ACH = ach_map[d["αεροστεγανότητα"]]
    infiltration = 0.33 * ACH * volume * ΔΤ

    # =========================================================
    # INTERNAL GAINS
    # =========================================================
    internal = ΕΣΩΤΕΡΙΚΑ[d["τύπος"]]

    # =========================================================
    # TOTAL LOAD
    # =========================================================
    if mode == "heating":
        total = transmission + infiltration - solar_gain - internal
    else:
        total = transmission + infiltration + solar_gain + internal

    total = max(total, 0)  # prevent negative loads

    return total / 1000, total * 3.412
