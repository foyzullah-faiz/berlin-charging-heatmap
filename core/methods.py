import pandas as pd
import geopandas as gpd
import core.HelperTools as ht
import folium
import streamlit as st
from streamlit_folium import folium_static
from branca.colormap import LinearColormap

def sort_by_plz_add_geometry(dfr, dfg, pdict): 
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()
    
    sorted_df               = dframe\
        .sort_values(by='PLZ')\
        .reset_index(drop=True)\
        .sort_index()
        
    sorted_df2              = sorted_df.merge(df_geo, on=pdict["geocode"], how ='left')
    sorted_df3              = sorted_df2.dropna(subset=['geometry'])
    
    sorted_df3['geometry']  = gpd.GeoSeries.from_wkt(sorted_df3['geometry'])
    ret                     = gpd.GeoDataFrame(sorted_df3, geometry='geometry')
    
    return ret

# -----------------------------------------------------------------------------
@ht.timer
def preprop_lstat(dfr, dfg, pdict):
    """Preprocessing dataframe from Ladesaeulenregister.csv"""
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()
    
    dframe2                 = dframe.loc[:,['Postleitzahl', 'Bundesland', 'Breitengrad', 'Längengrad', 'Nennleistung Ladeeinrichtung [kW]']]
    dframe2.rename(columns  = {"Nennleistung Ladeeinrichtung [kW]":"KW", "Postleitzahl": "PLZ"}, inplace = True)

    # Convert to string to match other dataframes
    dframe2['Breitengrad']  = dframe2['Breitengrad'].astype(str)
    dframe2['Längengrad']   = dframe2['Längengrad'].astype(str)
    dframe2['PLZ']          = dframe2['PLZ'].astype(str) # Ensure PLZ is string

    # Replace commas with periods for coordinates
    dframe2['Breitengrad']  = dframe2['Breitengrad'].str.replace(',', '.')
    dframe2['Längengrad']   = dframe2['Längengrad'].str.replace(',', '.')

    # FIX: Convert to int ONLY for the comparison to prevent crash
    dframe3                 = dframe2[(dframe2["Bundesland"] == 'Berlin') & 
                                      (pd.to_numeric(dframe2["PLZ"], errors='coerce') > 10115) &  
                                      (pd.to_numeric(dframe2["PLZ"], errors='coerce') < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret
    

# -----------------------------------------------------------------------------
@ht.timer
def count_plz_occurrences(df_lstat2):
    """Counts loading stations per PLZ"""
    # Group by PLZ and count occurrences, keeping geometry
    result_df = df_lstat2.groupby('PLZ').agg(
        Number=('PLZ', 'count'),
        geometry=('geometry', 'first')
    ).reset_index()
    
    return result_df

# -----------------------------------------------------------------------------
@ht.timer
def preprop_resid(dfr, dfg, pdict):
    """Preprocessing dataframe from plz_einwohner.csv"""
    dframe                  = dfr.copy()
    df_geo                  = dfg.copy()    
    
    dframe2                 = dframe.loc[:,['plz', 'einwohner', 'lat', 'lon']]
    dframe2.rename(columns  = {"plz": "PLZ", "einwohner": "Einwohner", "lat": "Breitengrad", "lon": "Längengrad"}, inplace = True)

    dframe2['PLZ']          = dframe2['PLZ'].astype(str)

    # FIX: Convert to int ONLY for the comparison
    dframe3                 = dframe2[ 
                                      (pd.to_numeric(dframe2["PLZ"], errors='coerce') > 10000) &  
                                      (pd.to_numeric(dframe2["PLZ"], errors='coerce') < 14200)]
    
    ret = sort_by_plz_add_geometry(dframe3, df_geo, pdict)
    
    return ret


# -----------------------------------------------------------------------------
@ht.timer
def make_streamlit_electric_Charging_resid(dfr1, dfr2):
    """Makes Streamlit App with Heatmap of Electric Charging Stations and Residents"""
    
    dframe1 = dfr1.copy()
    dframe2 = dfr2.copy()

    # Streamlit app
    st.title('Heatmaps: Electric Charging Stations and Residents')

    layer_selection = st.radio("Select Layer", ("Residents", "Charging_Stations"))

    # Create a Folium map
    m = folium.Map(location=[52.52, 13.40], zoom_start=10)

    if layer_selection == "Residents":
        
        # Create a color map for Residents
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe2['Einwohner'].min(), vmax=dframe2['Einwohner'].max())

        # Add polygons to the map for Residents
        for idx, row in dframe2.iterrows():
            if row['geometry']:
                folium.GeoJson(
                    row['geometry'],
                    style_function=lambda x, color=color_map(row['Einwohner']): {
                        'fillColor': color,
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7
                    },
                    tooltip=f"PLZ: {row['PLZ']}, Einwohner: {row['Einwohner']}"
                ).add_to(m)
        
        color_map.add_to(m)

    else:
        # Create a color map for Charging Stations
        color_map = LinearColormap(colors=['yellow', 'red'], vmin=dframe1['Number'].min(), vmax=dframe1['Number'].max())

        # Add polygons to the map for Numbers
        for idx, row in dframe1.iterrows():
            if row['geometry']:
                folium.GeoJson(
                    row['geometry'],
                    style_function=lambda x, color=color_map(row['Number']): {
                        'fillColor': color,
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7
                    },
                    tooltip=f"PLZ: {row['PLZ']}, Stations: {row['Number']}"
                ).add_to(m)
        
        color_map.add_to(m)
    
    folium_static(m, width=800, height=600)