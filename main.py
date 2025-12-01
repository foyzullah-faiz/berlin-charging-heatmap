import streamlit as st
import pandas                        as pd
import os

# -----------------------------------------------------------------------------
from core import methods             as m1
from core import HelperTools         as ht
from config                          import pdict

# -----------------------------------------------------------------------------
currentWorkingDirectory = os.getcwd()
os.chdir(currentWorkingDirectory)

# -----------------------------------------------------------------------------
@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""

    # 1. Load Geodata 
    df_geodat_plz   = pd.read_csv(pdict["file_geodat_plz"], sep=";", dtype={"PLZ": str})
    
    # FIX: Convert Geodata PLZ to Numeric so it matches the other dataframes for merging
    df_geodat_plz['PLZ'] = pd.to_numeric(df_geodat_plz['PLZ'], errors='coerce')

    # 2. Load Charging Stations
    df_lstat        = pd.read_csv(
                        pdict["file_lstations"], 
                        sep=";", 
                        skiprows=10, 
                        encoding="latin1", 
                        dtype={"Postleitzahl": str}
                      )
    
    # FIX: Convert Stations PLZ to Numeric for filtering logic in methods.py
    df_lstat['Postleitzahl'] = pd.to_numeric(df_lstat['Postleitzahl'], errors='coerce')
    
    # 3. Preprocess Stations
    df_lstat2       = m1.preprop_lstat(df_lstat, df_geodat_plz, pdict)
    
    # 4. Count Occurrences
    gdf_lstat3      = m1.count_plz_occurrences(df_lstat2)
    
    # 5. Load Residents
    df_residents    = pd.read_csv(pdict["file_residents"], dtype={"plz": str, "einwohner": int})
    
    # FIX: Convert Residents PLZ to Numeric
    df_residents['plz'] = pd.to_numeric(df_residents['plz'], errors='coerce')
    
    # 6. Preprocess Residents
    gdf_residents2  = m1.preprop_resid(df_residents, df_geodat_plz, pdict)
    
# -----------------------------------------------------------------------------------------------------------------------

    # 7. Generate Visualization
    m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)


if __name__ == "__main__": 
    main()