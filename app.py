# -*- coding: utf-8 -*-
import streamlit as st
from utils import *

# =========================================================
# UI CONFIGURATION
# =========================================================
st.set_page_config(page_title="Υπολογιστής Ενεργειακών Απαιτήσεων HVAC", layout="centered")
st.title("Υπολογιστής ενεργειακών απαιτήσεων για κλιματισμό")

mode = st.radio("Λειτουργία", ["ψύξη", "θέρμανση"])

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

βάση_val, kenak_zone_label = 210, "N/A"
ηλιακή_έκθεση_val = 1.0

if mode == "ψύξη":
    with c2:
        νομός = st.selectbox("Νομός / Περιοχή", list(ΝΟΜΟΙ_ΖΩΝΗ.keys()))
        υψόμετρο_500 = st.checkbox("Υψόμετρο > 500 μέτρα")
        _, effective_zone, βάση_val = compute_kenak_zone(νομός, υψόμετρο_500)
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
    εξωτερικοί = st.selectbox("Πλήθος εξωτερικών τοίχων", list(ΤΟΙΧΟΙ.keys()))
    μη_θερμαινόμενοι = st.selectbox("Τοίχοι σε επαφή με μη θερμαινόμενους χώρους", list(ΜΗ_ΘΕΡΜΑΙΝΟΜΕΝΟΙ.keys()))
    αεροστεγανότητα = st.selectbox("Ποιότητα αεροστεγανότητας", list(ΑΕΡΟΔΙΕΙΣΔΥΣΗ.keys()))
with c6:
    # Dynamic Insulation for Roof (Logic changed to 'άλλο διαμέρισμα')
    if οροφή_επαφή == "άλλο διαμέρισμα":
        μόνωση_οροφής = "άλλο διαμέρισμα"
        st.write("⬆️ *Οροφή: Δεν απαιτείται μόνωση (επαφή με θερμαινόμενο χώρο).*")
    else:
        μόνωση_οροφής = st.selectbox("Θερμομόνωση οροφής", list(U_ΟΡΟΦΗΣ_BASE.keys()))

    # Dynamic Insulation for Floor (Logic changed to 'άλλο διαμέρισμα')
    if δάπεδο_επαφή == "άλλο διαμέρισμα":
        μόνωση_δάπεδου = "άλλο διαμέρισμα"
        st.write("⬇️ *Δάπεδο: Δεν απαιτείται μόνωση (επαφή με θερμαινόμενο χώρο).*")
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

st.header("Συνήθης χρήση κλιματιστικού")
περιστασιακή = st.checkbox("Προτιμάτε περιστασιακή χρήση;")
αθόρυβη = st.checkbox("Προτιμάτε αθόρυβη λειτουργία;")

d = {
    "μόνωση": μόνωση_τοίχου, "μόνωση_οροφής": μόνωση_οροφής, "μόνωση_δάπεδου": μόνωση_δάπεδου,
    "επιφάνεια": επιφάνεια, "ύψος": ύψος, "εσωτερική": εσωτερική, "εξωτερική": εξωτερική, 
    "τύπος": τύπος, "δάπεδο": δάπεδο_επαφή, "οροφή": οροφή_επαφή, "εξωτερικοί": εξωτερικοί, 
    "μη_θερμαινόμενοι": μη_θερμαινόμενοι, "κουφώματα": κουφώματα, "αεροστεγανότητα": αεροστεγανότητα, 
    "μεγάλα": μεγάλα, "μικρά": μικρά, "μπαλκονόπορτες": μπαλκονόπορτες, "μονές": μονές, 
    "συρόμενες": συρόμενες, "ηλιακή_έκθεση": ηλιακή_έκθεση_val, "βάση_ακτινοβολίας": βάση_val,
    "βόρειος": βόρειος, "περιστασιακή": περιστασιακή, "αθόρυβη": αθόρυβη, "kenak_label": kenak_zone_label,
}

if st.button("Υπολογισμός"):
    try:
        kw, load_btu, nominal_btu_base, nominal_btu_final, unit_penalty_factors, breakdown, f_derating = υπολογισμός(d, mode)
        commercial_range_base = get_commercial_range(nominal_btu_base)
        commercial_range_final = get_commercial_range(nominal_btu_final)

        st.divider()
        st.success(f"**Φορτίο αιχμής:** {kw:.2f} kW | {load_btu:.0f} BTU/h")
        
        st.subheader("Ανάλυση φορτίου")
        for label, watts in breakdown.items():
            if watts > 0:
                st.write(f"**{label}:** {watts/1000:.2f} kW")

        st.divider()
        st.subheader("Πρόταση Κλιματιστικού")
        st.info(f"Βασική σύσταση: {commercial_range_base} BTU")
        if unit_penalty_factors:
            st.success(f"**Τελική σύσταση (με προτιμήσεις): {commercial_range_final} BTU**")
            
    except Exception as e:
        st.error(f"Σφάλμα κατά τον υπολογισμό. Βεβαιωθείτε ότι όλα τα πεδία είναι συμπληρωμένα.")
