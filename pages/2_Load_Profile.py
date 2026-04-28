import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from utils import υπολογισμός

st.set_page_config(page_title="Load Profile vs Temperature", layout="centered")
st.title("Load profile across ambient temperatures")

if "hvac_inputs" not in st.session_state:
    st.warning("Run the main calculator first — your room parameters will be loaded automatically.")
    st.stop()

base = dict(st.session_state["hvac_inputs"])

# ── Indoor setpoints ────────────────────────────────────────────────
st.header("Indoor setpoints")
c1, c2 = st.columns(2)
with c1:
    t_heat_in = st.number_input("Heating indoor setpoint (°C)", value=21)
with c2:
    t_cool_in = st.number_input("Cooling indoor setpoint (°C)", value=24)

# ── Ambient temperature range ───────────────────────────────────────
st.header("Ambient temperature range to plot")
c3, c4 = st.columns(2)
with c3:
    t_min = st.number_input("Minimum outdoor temp (°C)", value=-10)
with c4:
    t_max = st.number_input("Maximum outdoor temp (°C)", value=42)

# ── Climate distribution — user defined ─────────────────────────────
st.header("Your local climate (for percentile sizing)")
st.caption("Used only to place the design-point marker — does not affect the load curves.")

c5, c6 = st.columns(2)
with c5:
    st.subheader("Winter")
    t_heat_mean = st.number_input("Typical winter temp — median (°C)", value=8)
    t_heat_p10  = st.number_input("Coldest 10% of winter days (°C)", value=1,
                                   help="The temperature you expect to fall below only ~10% of winter hours.")
with c6:
    st.subheader("Summer")
    t_cool_mean = st.number_input("Typical summer temp — median (°C)", value=30)
    t_cool_p90  = st.number_input("Hottest 10% of summer days (°C)", value=38,
                                   help="The temperature exceeded only ~10% of summer hours.")

pct = st.slider("Design coverage (%)", 70, 99, 90,
                help="90% means the unit handles all but the most extreme 10% of hours.")

# ── Derive design temperatures from the distribution ────────────────
# We fit a normal to the two user-supplied points (median + P10/P90)
z_ref = norm.ppf(0.10)   # = -1.282, used as the reference percentile for the extreme input
z_design = norm.ppf(1 - pct / 100)

heat_std  = (t_heat_mean - t_heat_p10) / abs(z_ref)
cool_std  = (t_cool_p90  - t_cool_mean) / abs(z_ref)

t_heat_design = t_heat_mean + z_design * heat_std   # lower tail
t_cool_design = t_cool_mean - z_design * cool_std   # upper tail

# ── Solar settings for cooling curve ────────────────────────────────
# Use whatever was set in tool 1; fall back to neutral defaults
base.setdefault("βάση_ακτινοβολίας", 210)
base.setdefault("ηλιακή_έκθεση", 1.0)
base.setdefault("kenak_label", "N/A")   # no zone multiplier applied when "N/A"

# ── Build load curves ────────────────────────────────────────────────
temps = np.arange(t_min, t_max + 1, 0.5)

heat_loads, cool_loads = [], []
for t in temps:
    d = dict(base)
    d["εσωτερική"] = t_heat_in
    d["εξωτερική"] = float(t)
    kw, *_ = υπολογισμός(d, "θέρμανση")
    heat_loads.append(kw)

    d["εσωτερική"] = t_cool_in
    d["εξωτερική"] = float(t)
    kw, *_ = υπολογισμός(d, "ψύξη")
    cool_loads.append(kw)

# ── Balance point (intersection) ─────────────────────────────────────
diff = np.array(heat_loads) - np.array(cool_loads)
sign_changes = np.where(np.diff(np.sign(diff)))[0]
balance_points = []
for idx in sign_changes:
    t_bal = float(np.interp(0, [diff[idx], diff[idx+1]], [temps[idx], temps[idx+1]]))
    kw_bal = float(np.interp(t_bal, temps, heat_loads))
    balance_points.append((t_bal, kw_bal))

# ── Read load at design temperatures ────────────────────────────────
kw_at_heat_design = float(np.interp(t_heat_design, temps, heat_loads))
kw_at_cool_design = float(np.interp(t_cool_design, temps, cool_loads))

# ── Plot ─────────────────────────────────────────────────────────────
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=temps, y=heat_loads,
    name="Heating load", mode="lines",
    line=dict(color="#1f77b4", width=2)
))
fig.add_trace(go.Scatter(
    x=temps, y=cool_loads,
    name="Cooling load", mode="lines",
    line=dict(color="#d62728", width=2)
))

# Balance point(s)
for t_bal, kw_bal in balance_points:
    fig.add_vline(x=t_bal, line=dict(color="gray", dash="dot", width=1))
    fig.add_annotation(x=t_bal, y=kw_bal, text=f"Balance {t_bal:.1f}°C",
                       showarrow=True, arrowhead=2, font=dict(size=11, color="gray"))

# Heating design marker
fig.add_vline(x=t_heat_design, line=dict(color="#1f77b4", dash="dash", width=1.5))
fig.add_annotation(x=t_heat_design, y=kw_at_heat_design,
                   text=f"{pct}% heating<br>{t_heat_design:.1f}°C → {kw_at_heat_design:.2f} kW",
                   showarrow=True, arrowhead=2, font=dict(size=11, color="#1f77b4"),
                   bgcolor="white")

# Cooling design marker
fig.add_vline(x=t_cool_design, line=dict(color="#d62728", dash="dash", width=1.5))
fig.add_annotation(x=t_cool_design, y=kw_at_cool_design,
                   text=f"{pct}% cooling<br>{t_cool_design:.1f}°C → {kw_at_cool_design:.2f} kW",
                   showarrow=True, arrowhead=2, font=dict(size=11, color="#d62728"),
                   bgcolor="white")

fig.update_layout(
    xaxis_title="Outdoor temperature (°C)",
    yaxis_title="Load (kW)",
    legend=dict(orientation="h", y=1.08),
    margin=dict(t=60),
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

# ── Sizing summary ───────────────────────────────────────────────────
st.divider()
st.subheader(f"Sizing recommendation at {pct}% coverage")
c7, c8 = st.columns(2)
with c7:
    st.metric("Heating design load",
              f"{kw_at_heat_design:.2f} kW",
              f"{kw_at_heat_design * 3412:.0f} BTU/h")
    st.caption(f"Design temperature: {t_heat_design:.1f}°C")
with c8:
    st.metric("Cooling design load",
              f"{kw_at_cool_design:.2f} kW",
              f"{kw_at_cool_design * 3412:.0f} BTU/h")
    st.caption(f"Design temperature: {t_cool_design:.1f}°C")

governing = max(kw_at_heat_design, kw_at_cool_design)
st.info(
    f"**Governing load: {governing:.2f} kW ({governing * 3412:.0f} BTU/h)** — "
    f"size the unit for this value if a single reversible heat pump serves both modes."
)

st.markdown("---")
st.caption(
    "The load curves use all room parameters from the main calculator. "
    "The design-point markers are derived from a normal distribution fitted to your two climate inputs. "
    "This is an estimate — consult a licensed engineer for final sizing."
)
