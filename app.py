import streamlit as st

# -----------------------------
# Standard opening areas (m²)
# -----------------------------
OPENINGS = {
    "single_door": 0.90 * 2.10,   # 1.89 m²
    "double_door": 1.40 * 2.10,   # 2.94 m²
    "balcony_door": 1.60 * 2.10,  # 3.36 m²
    "large_window": 1.20 * 1.40,  # 1.68 m²
    "small_window": 0.60 * 0.60,  # 0.36 m²
}

# -----------------------------
# Multipliers
# -----------------------------
SUN_FACTOR = {
    "shaded": 0.85,
    "normal": 1.0,
    "high": 1.2
}

AIR_TIGHTNESS = {
    "good": 0.9,
    "normal": 1.0,
    "leaky": 1.15
}

ROOF_EXPOSURE = {
    "no": 1.0,
    "yes": 1.2
}

# NEW: insulation / building quality
BUILDING_QUALITY = {
    "old": 1.25,        # no insulation / old windows
    "average": 1.0,     # typical Greek apartment
    "modern": 0.85,     # insulated + better windows
    "high_perf": 0.7    # rare high efficiency
}

# -----------------------------
# Cooling load calculation
# -----------------------------
def calculate_load(data):
    area = data["area"]
    height = data["height"]
    volume = area * height

    # Temperature difference (NEW KEY FACTOR)
    delta_t = data["outdoor_temp"] - data["indoor_temp"]
    delta_t = max(delta_t, 5)  # safety floor

    # Base heat gain (improved physics approximation)
    # 30–45 W/m³ depending on ΔT
    base_factor = 30 + (delta_t - 10) * 1.2
    base_factor = max(base_factor, 25)

    base = volume * base_factor

    # -----------------------------
    # Openings
    # -----------------------------
    window_area = (
        data["large_window"] * OPENINGS["large_window"] +
        data["small_window"] * OPENINGS["small_window"] +
        data["balcony_door"] * OPENINGS["balcony_door"]
    )

    door_area = (
        data["single_door"] * OPENINGS["single_door"] +
        data["double_door"] * OPENINGS["double_door"]
    )

    total_openings = window_area + door_area

    # -----------------------------
    # Solar gains (dominant factor)
    # -----------------------------
    solar_gain = total_openings * 260  # W/m² peak sun gain

    solar_gain *= SUN_FACTOR[data["sun"]]

    # -----------------------------
    # Apply system modifiers
    # -----------------------------
    base *= AIR_TIGHTNESS[data["airtightness"]]
    base *= ROOF_EXPOSURE[data["roof"]]
    base *= BUILDING_QUALITY[data["building_quality"]]

    # -----------------------------
    # Total load
    # -----------------------------
    total_watts = base + solar_gain

    kw = total_watts / 1000
    btu = total_watts * 3.412

    return kw, btu, total_openings


# -----------------------------
# UI
# -----------------------------
st.title("Υπολογιστής Κλιματιστικού Δωματίου (Έκδοση 2)")

st.header("1. Διαστάσεις Δωματίου")
area = st.number_input("Επιφάνεια δωματίου (m²)", 5.0, 200.0, 20.0)
height = st.number_input("Ύψος δωματίου (m)", 2.0, 4.5, 2.8)

st.header("2. Θερμοκρασίες")

indoor_temp = st.number_input("Επιθυμητή θερμοκρασία δωματίου (°C)", 20, 28, 24)
outdoor_temp = st.number_input("Μέγιστη καλοκαιρινή εξωτερική θερμοκρασία (°C)", 30, 45, 35)

st.header("3. Παράθυρα & Πόρτες")

large_window = st.number_input("Μεγάλα παράθυρα", 0, 20, 2)
small_window = st.number_input("Μικρά παράθυρα", 0, 20, 1)
balcony_door = st.number_input("Μπαλκονόπορτες", 0, 5, 0)

single_door = st.number_input("Μονές πόρτες", 0, 5, 1)
double_door = st.number_input("Διπλές πόρτες", 0, 5, 0)

st.header("4. Συνθήκες")

sun = st.selectbox("Έκθεση στον ήλιο", ["σκιασμένο", "κανονικό", "έντονη_ηλιοφάνεια"])
airtightness = st.selectbox("Αεροστεγανότητα", ["καλή", "μέτρια", "κακή"])
roof = st.selectbox("Δωμάτιο κάτω από στέγη;", ["όχι", "ναι"])

building_quality = st.selectbox(
    "Ποιότητα κατασκευής / μόνωσης",
    ["old", "average", "modern", "high_perf"]
)

# -----------------------------
# Data pack
# -----------------------------
data = {
    "area": area,
    "height": height,
    "indoor_temp": indoor_temp,
    "outdoor_temp": outdoor_temp,
    "large_window": large_window,
    "small_window": small_window,
    "balcony_door": balcony_door,
    "single_door": single_door,
    "double_door": double_door,
    "sun": sun,
    "airtightness": airtightness,
    "roof": roof,
    "building_quality": building_quality
}

# -----------------------------
# Result
# -----------------------------
if st.button("Υπολογισμός Κλιματιστικού"):
    kw, btu, opening_area = calculate_load(data)

    st.subheader("Αποτέλεσμα")

    st.write(f"Συνολική επιφάνεια ανοιγμάτων: {opening_area:.2f} m²")
    st.write(f"Ψυκτικό φορτίο: {kw:.2f} kW")
    st.write(f"Ψυκτικό φορτίο: {btu:.0f} BTU/h")

    # Recommendation logic
    if kw < 2.5:
        st.success("Προτεινόμενο κλιματιστικό: ~9.000 BTU")
    elif kw < 3.5:
        st.success("Προτεινόμενο κλιματιστικό: ~12.000 BTU")
    elif kw < 5:
        st.success("Προτεινόμενο κλιματιστικό: ~18.000 BTU")
    else:
        st.success("Προτεινόμενο κλιματιστικό: 24.000+ BTU")
