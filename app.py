import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np


from src.seismology import b_value


st.set_page_config(page_title="Greek Earthquake Explorer", layout = "wide")


st.title("Greek Earthquake Explorer")
st.write("Earthquakes in and around Greece since 2000, from the USGS catalog.")




@st.cache_data
def load_data():
    eq = pd.read_csv("data/earthquakes.csv", parse_dates=["time"])
    eq["year"] = eq["time"].dt.year
    return eq

eq = load_data()


#~~~~~~sidebar filters
st.sidebar.header("Filters")
years = st.sidebar.slider(
    "Years",
    min_value=int(eq["year"].min()),
    max_value=int(eq["year"].max()),
    value = (2009, int(eq["year"].max())),
)


magnitude = st.sidebar.slider("Magnitude",2.5, 7.5, (4.2, 7.5), step =0.1)   
depth = st.sidebar.slider("Depth (km)", 0, int(eq["depth"].max()) + 1, (0, int(eq["depth"].max()) + 1))

filtered = eq[
    (eq["year"].between(*years))
    & (eq["mag"].between(*magnitude))
    & (eq["depth"].between(*depth))
]
st.sidebar.write(f"Showing {len(filtered):,} of {len(eq):,} earthquakes")

#~~~~~Metric tiles
col1, col2, col3 = st.columns(3)
col1.metric("Earthquakes", f"{len(filtered):,}")
col2.metric("Largest Magnitude", filtered["mag"].max())
col3.metric("Years covered", f"{years[0]}-{years[1]}")

#~~~~~~Map
st.subheader("Map")
fig = px.scatter_map(
    filtered,
    lat="latitude",
    lon="longitude",
    size="mag",
    color="depth",
    hover_name="place",
    hover_data={"mag": True, "depth": True, "time": True, "latitude": False, "longitude": False},
    color_continuous_scale="Viridis_r",
    size_max=12,
    zoom=5,
    center={"lat": 38.5, "lon": 24.5},
    height=600,
)
st.plotly_chart(fig, use_container_width=True)

#~~~~Charts
st.subheader("Activity over time")
monthly = (
    filtered.set_index("time")
    .resample("MS")
    .size()
    .rename("earthquakes")
    .reset_index()
)
fig_time = px.bar(monthly, x="time", y="earthquakes")
fig_time.update_layout(xaxis_title="Month", yaxis_title="Number of earthquakes", height=350)
st.plotly_chart(fig_time, use_container_width=True)

st.subheader("Largest earthquakes in this selection")
top10 = filtered.nlargest(10, "mag")[["time", "mag", "depth", "place"]]
st.dataframe(top10, hide_index=True, use_container_width=True)

st.subheader("Gutenberg-Richter distribution")
st.write(
    "The number of earthquakes falls off exponentially with magnitude."
    "Above the magnitude of completeness (Mc), the cumulative counts follow a straight line"
    "on a log scale, and its slope is the b-value. Move the Mc slider to see how sensitive it is"

)
mc_app = st.slider("Magnitude of completeness (Mc)", 2.5, 6.0, 4.2, step=0.1)
mags = filtered["mag"].round(1)
freq = mags.value_counts().sort_index()
cumulative= freq[::-1].cumsum()[::-1]
gr = pd.DataFrame({"magnitude": cumulative.index, "count":cumulative.values})
b, err, n=b_value(mags, mc_app)
if n < 50:
    st.warning("Fewer than 50 earthquakes above this Mc, so the b-value is not reliable.  Lower Mc or widen the filters.")
else:
    a =np.log10(n) + b * mc_app
    m_line = np.linspace(mc_app, mags.max(), 50)
    n_line= 10 ** (a- b * m_line)
    
    c1 , c2 = st.columns(2)
    c1.metric("b-value", f"{b:.2f} ± {err:.2f}")
    c2.metric("Earthquakes used (M ≥ Mc) ", f"{n:,}")
    
    fig_gr = px.scatter(gr, x="magnitude", y="count", log_y=True)
    fig_gr.add_scatter(x=m_line, y=n_line, mode="lines", name=f"Fit: b = {b:.2f}")
    fig_gr.add_vline(x=mc_app, line_dash="dash", annotation_text=f"Mc = {mc_app}")
    fig_gr.update_layout(xaxis_title="Magnitude", yaxis_title="Number of earthquakes (M or larger)", height=450)
    st.plotly_chart(fig_gr, use_container_width=True)


#~~~~~~Data table

st.subheader("Sample of the data")
st.dataframe(filtered[["time", "latitude", "longitude", "depth", "mag"]])
