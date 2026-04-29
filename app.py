# -*- coding: utf-8 -*-
import streamlit as st
from utils import *

# =========================================================
# UI CONFIGURATION
# =========================================================
st.set_page_config(page_title="Υπολογιστής Ενεργειακών Απαιτήσεων HVAC", layout="centered")
st.title("Υπολογιστής ενεργειακών απαιτήσεων για κλιματισμό")

mode = st.radio("Λειτουργία", ["ψύξη", "θέρμανση"])

# Initialize temperatures based on mode
if "last_mode" not in st.session_state or st.session_state.last_mode != mode:
    st.session_state.last_mode = mode
    if mode == "ψύξη":
        st.session_state.tin, st.session_state.tout = 24, 38
    else:
        st.session_state.tin, st.session_state.tout = 21, 5

# --- Section: Κλιματικές συνθήκες ---
st.header("Κλιματικές συνθήκες")
c1, c2 = st.columns(2)

with c1:
    εσωτερική = st.number_input("Εσωτερική Θερμοκρασία (°C)", value=st.session_state.tin)
    εξωτερική = st.number_input("Εξωτερική Θερμοκρασία (°C)", value=st.session_state.tout)

# Defaults
ηλιακή_έκθεση_val, ηλιακή_έκθεση_label = 1.0, "N/A"
βάση_val, kenak_zone_label = 210, "N/A"
νομός, υψόμετρο_500 = "N/A", False
base_zone, effective_zone = "N/A", "N/A"

if mode == "ψύξη":
    with c2:
        νομός = st.selectbox("Νομός / Περιοχή", list(ΝΟΜΟΙ_ΖΩΝΗ.keys()))
        υψόμετρο_500 = st.checkbox("Υψόμετρο > 500 μέτρα")
        base_zone, effective_zone, βάση_val = compute_kenak_zone(νομός, υψόμετρο_500)
        kenak_zone_label = f"Ζώνη {effective_zone}"
        ηλιακή_έκθεση_label = st.selectbox("Ηλιακή έκθεση", list(ΗΛΙΑΚΗ_ΕΚΘΕΣΗ.keys()))
        ηλιακή_έκθεση_val = ΗΛΙΑΚΗ_ΕΚΘΕΣΗ[ηλιακή_έκθεση_label]
else:
    with c2:
        st.info("Στη θέρμανση τα ηλιακά κέρδη παραλείπονται για το φορτίο αιχμής.")

# --- Section: Περιγραφή χώρου ---
st.header("Περιγραφή χώρου")
c3, c4 = st.columns(2)
with c3:
    επιφάνεια = st.number_input("Επιφάνεια χώρου (m²)", 5, 500, 20)
    ύψος = st.number_input("Ύψος χώρου (m)", 2.0, 4.5, 2.8)
with c4:
    τύπος = st.selectbox("Χρήση χώρου", list(ΕΣΩΤΕΡΙΚΑ.keys()))
    δάπεδο_επαφή = st.selectbox("Δάπεδο σε επαφή με", ΔΑΠΕΔΟ)
    οροφή_επαφή = st.selectbox("Οροφή σε επαφή με", ΟΡΟΦΗ)
    βόρειος = st.checkbox("Βόρειος προσανατολισμός") if mode == "θέρμανση" else False

# --- Section: Δομικά στοιχεία ---
st.header("Δομικά στοιχεία")
μόνωση_τοίχου = st.selectbox("Θερμομόνωση τοίχων", list(U_ΤΟΙΧΟΥ.keys()))

c5, c6 = st.columns(2)
with c5:
    εξωτερικοί = st.number_input("Πλήθος εξωτερικών τοίχων", 1, 4, 1)
    μη_θερμαινόμενοι = st.number_input("Τοίχοι σε επαφή με μη θερμαινόμενους χώρους", 0, 3, 0)
    αεροστεγανότητα = st.selectbox("Ποιότητα αεροστεγανότητας", list(ΑΕΡΟΔΙΕΙΣΔΥΣΗ.keys()))
with c6:
    # Handle Roof Insulation Logic
    if οροφή_επαφή == "άλλο διαμέρισμα":
        μόνωση_οροφής = "άλλο διαμέρισμα"
        st.write("⬆️ *Οροφή: Επαφή με θερμαινόμενο χώρο.*")
    else:
        μόνωση_οροφής = st.selectbox("Θερμομόνωση οροφής", list(U_ΟΡΟΦΗΣ_BASE.keys()))

    # Handle Floor Insulation Logic
    if δάπεδο_επαφή == "άλλο διαμέρισμα":
        μόνωση_δάπεδου = "άλλο διαμέρισμα"
        st.write("⬇️ *Δάπεδο: Επαφή με θερμαινόμενο χώρο.*")
    else:
        μόνωση_δάπεδου = st.selectbox("Θερμομόνωση δαπέδου", list(U_ΔΑΠΕΔΟΥ_BASE.keys()))

    κουφώματα = st.selectbox("Τύπος κουφωμάτων/υαλοπινάκων", list(ΚΟΥΦΩΜΑΤΑ.keys()))

st.write("**Πλήθος Ανοιγμάτων:**")
c7, c8, c9 = st.columns(3)
with c7:
    μεγάλα = st.number_input("Μεγάλα παράθυρα", 0, 20, 0)
    μονές = st.number_input("Μονές μπαλκ/πορτες", 0, 10, 0)
with c8:
    μικρά = st.number_input("Μικρά παράθυρα", 0, 20, 0)
    συρόμενες = st.number_input("Συρόμενες μπαλκ/πορτες", 0, 10, 0)
with c9:
    μπαλκονόπορτες = st.number_input("Διπλές ανοιγόμενες μπαλκ/πορτες", 0, 10, 1)

περιστασιακή = st.checkbox("Προτιμάτε περιστασιακή χρήση;")
αθόρυβη = st.checkbox("Προτιμάτε αθόρυβη λειτουργία;")

# Build the dictionary EXACTLY as utils.py expects it
d = {
    "μόνωση": μόνωση_τοίχου, 
    "μόνωση_οροφής": μόνωση_οροφής, 
    "μόνωση_δάπεδου": μόνωση_δάπεδου,
    "επιφάνεια": επιφάνεια, 
    "ύψος": ύψος, 
    "εσωτερική": εσωτερική, 
    "εξωτερική": εξωτερική, 
    "τύπος": τύπος, 
    "δάπεδο": δάπεδο_επαφή, 
    "οροφή": οροφή_επαφή, 
    "εξωτερικοί": εξωτερικοί, 
    "μη_θερμαινόμενοι": μη_θερμαινόμενοι, 
    "κουφώματα": κουφώματα, 
    "αεροστεγανότητα": αεροστεγανότητα, 
    "μεγάλα": μεγάλα, 
    "μικρά": μικρά, 
    "μπαλκονόπορτες": μπαλκονόπορτες, 
    "μονές": μονές, 
    "συρόμενες": συρόμενες, 
    "ηλιακή_έκθεση": ηλιακή_έκθεση_val, 
    "βάση_ακτινοβολίας": βάση_val,
    "βόρειος": βόρειος, 
    "περιστασιακή": περιστασιακή, 
    "αθόρυβη": αθόρυβη, 
    "kenak_label": kenak_zone_label,
}

if st.button("Υπολογισμός"):
    try:
        # Run Calculation
        kw, load_btu, nominal_btu_base, nominal_btu_final, unit_penalty_factors, breakdown, f_derating = υπολογισμός(d, mode)
        
        # SAVE TO SESSION STATE (This is what restores the Load Profile values)
        if mode == "θέρμανση":
            st.session_state["hvac_inputs_heating"] = d
        else:
            st.session_state["hvac_inputs_cooling"] = d
        
        # UI Display
        st.divider()
        st.success(f"**Φορτίο αιχμής:** {kw:.2f} kW | {load_btu:.0f} BTU/h")
        
        st.subheader("Ανάλυση φορτίου αιχμής")
        for label, watts in breakdown.items():
            if watts > 0:
                st.write(f"**{label}:** {watts/1000:.2f} kW")

        st.divider()
        st.subheader("Επιλογή μεγέθους κλιματιστικού")
        derating_pct = (1 - f_derating) * 100
        st.write(f"Λόγω μειωμένης απόδοσης στους **{εξωτερική}°C** (−{derating_pct:.0f}%), απαιτούνται **{nominal_btu_base:,.0f} BTU/h**.")

        if unit_penalty_factors:
            st.info(f"**Βασική σύσταση:** {commercial_range_base} BTU")
            st.warning("**Προσαυξήσεις λόγω χρήσης:**")
            for reason, factor in unit_penalty_factors.items():
                st.write(f"- {reason}: ×{factor:.2f}")
            st.success(f"**Τελική σύσταση (με προτιμήσεις): {commercial_range_final} BTU**")
        else:
            st.success(f"**Συνιστώμενη ισχύς: {commercial_range_base} BTU**")

        # --- RESTORED SUMMARY REPORT ---
        st.divider()
        unit_penalty_lines = "\n".join(f"  - {r}: ×{f:.2f}" for r, f in unit_penalty_factors.items()) or "  Καμία"
        
        report = f"""ΑΝΑΦΟΡΑ ΕΝΕΡΓΕΙΑΚΩΝ ΑΠΑΙΤΗΣΕΩΝ (Λειτουργία: {mode.upper()})
--------------------------------------------------
ΚΛΙΜΑΤΙΚΕΣ ΣΥΝΘΗΚΕΣ:
- Θερμοκρασία: Εσωτ. {εσωτερική}°C / Εξωτ. {εξωτερική}°C
- Ζώνη ΚΕΝΑΚ: {kenak_zone_label}
- Ηλιακή Έκθεση: {ηλιακή_έκθεση_label if mode == "ψύξη" else "N/A"}

ΠΕΡΙΓΡΑΦΗ ΧΩΡΟΥ:
- Χώρος: {τύπος} ({επιφάνεια}m² / {ύψος}m ύψος)
- Δάπεδο: {δάπεδο_επαφή}
- Οροφή: {οροφή_επαφή}
- Βόρειος Προσανατολισμός: {"Ναι (+15%)" if βόρειος else "Όχι"}

ΔΟΜΙΚΑ ΣΤΟΙΧΕΙΑ:
- Μόνωση τοίχων: {μόνωση_τοίχου}
- Εξωτερικοί τοίχοι: {εξωτερικοί}
- Τοίχοι με μη θερμαινόμενους: {μη_θερμαινόμενοι}
- Κουφώματα: {κουφώματα}

ΑΠΟΤΕΛΕΣΜΑΤΑ:
- Φορτίο αιχμής: {load_btu:.0f} BTU/h
- Ονομαστική ισχύς (Base): {nominal_btu_base:,.0f} BTU/h ({commercial_range_base} BTU)
- Προσαυξήσεις χρήσης:
{unit_penalty_lines}
- Τελική επιλογή: {commercial_range_final} BTU
--------------------------------------------------"""
        st.code(report, language="text")

        # --- RESTORED DISCLAIMER ---
        st.caption("**Αποποίηση Ευθύνης:** Ο παρών υπολογισμός αποτελεί εκτίμηση. "
                   "Για την οριστική μελέτη, απαιτείται αυτοψία από αδειούχο μηχανολόγο.")

    except Exception as e:
        st.error(f"Σφάλμα κατά τον υπολογισμό: {e}")
