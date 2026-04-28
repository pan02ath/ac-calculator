# -*- coding: utf-8 -*-
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from utils import υπολογισμός, get_commercial_range

st.set_page_config(page_title="Load Profile vs Temperature", layout="centered")
st.title("Προφίλ φορτίου ανά θερμοκρασία περιβάλλοντος")

has_heating = "hvac_inputs_heating" in st.session_state
has_cooling  = "hvac_inputs_cooling"  in st.session_state

if not has_heating and not has_cooling:
    st.warning(
        "Παρακαλώ εκτελέστε πρώτα το εργαλείο υπολογισμού απωλειών (σελίδα 1) — "
        "τα δεομένα θα εισαχθούν αυτόματα εδώ."
    )
    st.stop()

if has_heating and has_cooling:
    st.success("Έγινε εισαγωγή των στοιχείων που ορίσατε για θέρμανση και ψύξη.")
elif has_heating:
    st.info("Φορτωμένα μόνο στοιχεία θέρμανσης. Εκτελέστε τον υπολογιστή και σε λειτουργία ψύξης για πλήρες διάγραμμα.")
else:
    st.info("Φορτωμένα μόνο στοιχεία ψύξης. Εκτελέστε τον υπολογιστή και σε λειτουργία θέρμανσης για πλήρες διάγραμμα.")

base_heating = st.session_state.get("hvac_inputs_heating",
               st.session_state.get("hvac_inputs_cooling"))
base_cooling  = st.session_state.get("hvac_inputs_cooling",
               st.session_state.get("hvac_inputs_heating"))

base_cooling = dict(base_cooling)
base_heating = dict(base_heating)

base_cooling.setdefault("βάση_ακτινοβολίας", 210)
base_cooling.setdefault("ηλιακή_έκθεση", 1.0)
base_cooling.setdefault("kenak_label", "Ζώνη Β")

# ── Indoor setpoints ─────────────────────────────────────────────────
st.header("Επιθυμητή εσωτερική θερμοκρασία")
c1, c2 = st.columns(2)
with c1:
    t_heat_in = st.number_input("Setpoint θέρμανσης (°C)", value=21)
with c2:
    t_cool_in = st.number_input("Setpoint ψύξης (°C)", value=24)

# ── Ambient temperature range ────────────────────────────────────────
st.header("Εύρος θερμοκρασίας περιβάλλοντος")
c3, c4 = st.columns(2)
with c3:
    t_min = st.number_input("Ελάχιστη εξωτερική θερμοκρασία (°C)", value=-10)
with c4:
    t_max = st.number_input("Μέγιστη εξωτερική θερμοκρασία (°C)", value=42)

# ── Climate distribution ─────────────────────────────────────────────
st.header("Κλιματικά δεδομένα περιοχής για τον ορισμό του επιθυμητού εύρους λειτουργίας")
st.caption(
    "Εισάγετε δύο σημεία για κάθε εποχή — τη διάμεσο θερμοκρασία "
    "και το ακραίο 10% — ώστε να υπολογιστεί η απαιτούμενη ισχύς ψύξης και θέρμανσης  "
    "για το επιλεγμένο εύρος θερμοκρασιών."
)

c5, c6 = st.columns(2)
with c5:
    st.subheader("Χειμώνας")
    t_heat_mean = st.number_input(
        "Τυπική χειμερινή θερμ. — διάμεσος (°C)", value=8,
        help="Η πιο συνηθισμένη εξωτερική θερμοκρασία τον χειμώνα."
    )
    t_heat_p10 = st.number_input(
        "Ψυχρότερο 10% χειμερινών ωρών (°C)", value=1,
        help="Η θερμοκρασία κάτω από την οποία βρίσκεστε μόνο ~10% των χειμερινών ωρών."
    )
with c6:
    st.subheader("Καλοκαίρι")
    t_cool_mean = st.number_input(
        "Τυπική καλοκαιρινή θερμ. — διάμεσος (°C)", value=30,
        help="Η πιο συνηθισμένη εξωτερική θερμοκρασία το καλοκαίρι."
    )
    t_cool_p90 = st.number_input(
        "Θερμότερο 10% καλοκαιρινών ωρών (°C)", value=38,
        help="Η θερμοκρασία που ξεπερνιέται μόνο ~10% των καλοκαιρινών ωρών."
    )

pct = st.slider(
    "Ποσοστό κάλυψης (%)", 70, 99, 90,
    help="90% σημαίνει ότι η μονάδα καλύπτει όλες τις ώρες εκτός του ακραίου 10%."
)

# ── Derive design temperatures from normal distribution ──────────────
z_ref    = norm.ppf(0.10)
z_design = norm.ppf(1 - pct / 100)

heat_std = (t_heat_mean - t_heat_p10) / abs(z_ref)
cool_std = (t_cool_p90  - t_cool_mean) / abs(z_ref)

t_heat_design = t_heat_mean + z_design * heat_std
t_cool_design = t_cool_mean - z_design * cool_std

# ── Build load curves ─────────────────────────────────────────────────
temps = np.arange(t_min, t_max + 0.5, 0.5)

heat_loads, cool_loads = [], []
for t in temps:
    dh = dict(base_heating)
    dh["εσωτερική"] = t_heat_in
    dh["εξωτερική"] = float(t)
    kw, *_ = υπολογισμός(dh, "θέρμανση")
    heat_loads.append(kw)

    dc = dict(base_cooling)
    dc["εσωτερική"] = t_cool_in
    dc["εξωτερική"] = float(t)
    kw, *_ = υπολογισμός(dc, "ψύξη")
    cool_loads.append(kw)

heat_loads = np.array(heat_loads)
cool_loads = np.array(cool_loads)

# ── Balance point (intersection) ─────────────────────────────────────
diff = heat_loads - cool_loads
sign_changes = np.where(np.diff(np.sign(diff)))[0]
balance_points = []
for idx in sign_changes:
    t_bal  = float(np.interp(0, [diff[idx], diff[idx + 1]], [temps[idx], temps[idx + 1]]))
    kw_bal = float(np.interp(t_bal, temps, heat_loads))
    balance_points.append((t_bal, kw_bal))

# ── Read load at design temperatures ─────────────────────────────────
kw_at_heat_design = float(np.interp(t_heat_design, temps, heat_loads))
kw_at_cool_design = float(np.interp(t_cool_design, temps, cool_loads))

# ── Plot ──────────────────────────────────────────────────────────────
fig = go.Figure()

heat_mask = temps <= t_heat_in
cool_mask = temps >= t_cool_in

fig.add_vrect(x0=t_min, x1=t_heat_in, fillcolor="blue", opacity=0.05, line_width=0)
fig.add_vrect(x0=t_heat_in, x1=t_cool_in, fillcolor="green", opacity=0.05, line_width=0)
fig.add_vrect(x0=t_cool_in, x1=t_max, fillcolor="red", opacity=0.05, line_width=0)

fig.add_trace(go.Scatter(
    x=temps[heat_mask], y=heat_loads[heat_mask],
    name="Θέρμανση", mode="lines",
    line=dict(color="#1f77b4", width=2)
))
fig.add_trace(go.Scatter(
    x=temps[cool_mask], y=cool_loads[cool_mask],
    name="Ψύξη", mode="lines",
    line=dict(color="#d62728", width=2)
))

fig.add_trace(go.Scatter(
    x=[t_heat_design], y=[kw_at_heat_design],
    mode="markers+text",
    text=[f"{pct}% θέρμανση"],
    textposition="top center",
    marker=dict(size=10, color="#1f77b4"),
    showlegend=False
))
fig.add_trace(go.Scatter(
    x=[t_cool_design], y=[kw_at_cool_design],
    mode="markers+text",
    text=[f"{pct}% ψύξη"],
    textposition="top center",
    marker=dict(size=10, color="#d62728"),
    showlegend=False
))

fig.add_vline(x=t_heat_design, line=dict(color="#1f77b4", dash="dash", width=1))
fig.add_vline(x=t_cool_design, line=dict(color="#d62728", dash="dash", width=1))

if balance_points:
    mid = (t_heat_in + t_cool_in) / 2
    t_bal, kw_bal = min(balance_points, key=lambda x: abs(x[0] - mid))
    fig.add_trace(go.Scatter(
        x=[t_bal], y=[kw_bal],
        mode="markers+text",
        text=["Σημείο ισορροπίας"],
        textposition="bottom center",
        marker=dict(size=9, color="black"),
        showlegend=False
    ))
    fig.add_vline(x=t_bal, line=dict(color="gray", dash="dot", width=1))

fig.update_layout(
    xaxis_title="Εξωτερική θερμοκρασία (°C)",
    yaxis_title="Φορτίο (kW)",
    legend=dict(orientation="h", y=1.08),
    margin=dict(t=60),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ── Sizing summary ────────────────────────────────────────────────────
st.divider()
st.subheader(f"Σύσταση διαστασιολόγησης για {pct}% κάλυψη")

c7, c8 = st.columns(2)
with c7:
    st.metric(
        "Μέγιστο φορτίο θέρμανσης",
        f"{kw_at_heat_design:.2f} kW",
        f"{kw_at_heat_design * 3412:.0f} BTU/h"
    )
    st.caption(f"στους {t_heat_design:.1f}°C")
with c8:
    st.metric(
        "Μέγιστο φορτίο ψύξης",
        f"{kw_at_cool_design:.2f} kW",
        f"{kw_at_cool_design * 3412:.0f} BTU/h"
    )
    st.caption(f"στους: {t_cool_design:.1f}°C")

governing = max(kw_at_heat_design, kw_at_cool_design)
governing_btu = governing * 3412
recommended = get_commercial_range(governing_btu)

st.info(
    f"Οι παραπάνω τιμές αφορούν τις μέγιστες τιμές ισχύος ενός κλιματιστικού "
    f"ώστε να καλύπτονται οι ανάγκες θέρμανσης και ψύξης ενός χώρου για το δεδομένο εύρος θερμοκρασιών."
)

st.markdown("---")
st.caption(
    "Οι καμπύλες φορτίου βασίζονται στα δεδομένα που εισάγατε από την κύρια εφαρμογή. "
    "Τα παραπάνω αποτελούν εκτίμηση — απαιτείται αυτοψία από αδειούχο μηχανολόγο για μια οριστική μελέτη."
)
