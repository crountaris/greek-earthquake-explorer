import pandas as pd
import streamlit as st
import plotly.express as px


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



#~~~~~~Data table

st.subheader("Sample of the data")
st.dataframe(filtered[["time", "latitude", "longitude", "depth", "mag"]])
