import os
import pandas                        as pd
from core import methods             as m1
from core import HelperTools         as ht
from config                          import pdict

# -----------------------------------------------------------------------------
# Fix for Mac path (Task 2/3 requirement to run locally)
os.chdir(os.getcwd())
print("Current working directory\n" + os.getcwd())

# -----------------------------------------------------------------------------
@ht.timer
def main():
    """Main: Generation of Streamlit App for visualizing electric charging stations & residents in Berlin"""

    # 1. Load Geodata (Required by methods.py)
    df_geodat_plz   = pd.read_csv(pdict["file_geodat_plz"], sep=";", dtype={"PLZ": str})
    
    # 2. Load and Process Charging Stations
    # Load raw
    df_lstat_raw    = pd.read_csv(pdict["file_lstations"], sep=";", skiprows=10, encoding="latin1", dtype={"Postleitzahl": str})
    
    # Gap 1: Preprocess stations using core/methods.py
    # This filters for Berlin and adds geometry
    df_lstat2       = m1.preprop_lstat(df_lstat_raw, df_geodat_plz, pdict)
    
    # Gap 2: Count occurrences
    # This groups by PLZ to get the 'Number' of stations
    gdf_lstat3      = m1.count_plz_occurrences(df_lstat2)
    
    # 3. Load and Process Residents
    # Load raw
    df_residents_raw = pd.read_csv(pdict["file_residents"], dtype={"plz": str, "einwohner": int})
    
    # Gap 3: Preprocess residents using core/methods.py
    gdf_residents2  = m1.preprop_resid(df_residents_raw, df_geodat_plz, pdict)
    
    # -----------------------------------------------------------------------------------------------------------------------
    # 4. Generate Visualization
    # Use the professor's exact method for the Streamlit app
    m1.make_streamlit_electric_Charging_resid(gdf_lstat3, gdf_residents2)


if __name__ == "__main__": 
    main()