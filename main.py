import streamlit as st
import pandas as pd
import pydeck as pdk
import os

# -----------------------------------------------------------------------------
from core import methods             as m1
from core import HelperTools         as ht
from config                          import pdict

# -----------------------------------------------------------------------------
# FIX: Automatically detect the current folder
# This works on Mac, Windows, and Linux automatically.
currentWorkingDirectory = os.getcwd()

# -----------------------------------------------------------------------------
os.chdir(currentWorkingDirectory)
print("Current working directory\n" + os.getcwd())

# -----------------------------------------------------------------------------
@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""
    
    st.set_page_config(layout="wide", page_title="Berlin Charging Heatmap")
    st.title("⚡ Berlin Electric Charging Demand")

    # 1. Load Geodata
    df_geodat_plz   = pd.read_csv(pdict["file_geodat_plz"], sep=";", dtype={"PLZ": str})
    
    # 2. Load Charging Stations
    df_lstat        = pd.read_csv(
                        pdict["file_lstations"], 
                        sep=";", 
                        skiprows=10, 
                        encoding="latin1", 
                        dtype=str
                      )
    
    # 3. Preprocess Stations
    df_lstat.columns = df_lstat.columns.str.strip()
    if 'Postleitzahl' in df_lstat.columns:
        df_lstat.rename(columns={'Postleitzahl': 'PLZ'}, inplace=True)
        
    df_lstat2       = df_lstat[df_lstat['PLZ'].str.startswith('1', na=False)].copy()
    
    # 4. Aggregate
    gdf_lstat3      = df_lstat2.groupby('PLZ').size().reset_index(name='Station_Count')
    
    # 5. Load Residents
    df_residents    = pd.read_csv(pdict["file_residents"], dtype={"plz": str, "einwohner": int})
    
    # 6. Merge Everything
    gdf_residents2  = pd.merge(df_residents, df_geodat_plz, left_on='plz', right_on='PLZ', how='inner')
    gdf_residents2  = pd.merge(gdf_residents2, gdf_lstat3, on='PLZ', how='left')
    gdf_residents2['Station_Count'] = gdf_residents2['Station_Count'].fillna(0)
    gdf_residents2['Demand_Index'] = gdf_residents2['einwohner'] / (gdf_residents2['Station_Count'] + 1)
    
    # -----------------------------------------------------------------------------------------------------------------------
    # Visualization

    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Geospatial Heatmap")
        layer = pdk.Layer(
            "ColumnLayer",
            data=gdf_residents2,
            get_position=["lon", "lat"],
            get_elevation="Demand_Index",
            elevation_scale=0.5,
            radius=200,
            get_fill_color=[200, 30, 0, 160],
            pickable=True,
            auto_highlight=True,
        )
        view_state = pdk.ViewState(latitude=52.52, longitude=13.40, zoom=10, pitch=50)
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "PLZ: {PLZ}\nPopulation: {einwohner}\nStations: {Station_Count}\nDemand Index: {Demand_Index}"})
        st.pydeck_chart(r)

    with col2:
        st.subheader("High Demand Areas")
        st.dataframe(gdf_residents2[['PLZ', 'einwohner', 'Station_Count', 'Demand_Index']].sort_values(by='Demand_Index', ascending=False).head(10))


if __name__ == "__main__": 
    main()