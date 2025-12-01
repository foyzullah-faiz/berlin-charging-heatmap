## 3. Methodology

### **The Algorithm**
To quantify the "need" for infrastructure, we calculate a **Demand Index** for every Postal Code using the following logic:

1.  **Filter:** Isolate data rows where `PLZ` starts with "1..." (Berlin Region).
2.  **Aggregate:** Count total charging stations per PLZ.
3.  **Calculate:** Apply the demand formula:

$$\text{Demand Index} = \frac{\text{Population}}{\text{Station Count} + 1}$$

### **Visualization Strategy**
The project uses **Folium** to generate interactive 2D Heatmaps (Choropleth maps).
* **Layers:** The user can toggle between two views:
    1.  **Residents:** Color intensity represents population density.
    2.  **Charging Stations:** Color intensity represents the number of stations.
* **Color Scale:** Yellow (Low) to Red (High).

---

## 4. Analysis of Results (Task 7)

The geospatial analysis reveals a significant mismatch between population centers and infrastructure distribution.

### **A. Identified "Hotspots" (High Demand)**
The visualization shows that the highest demand is **not** in the city center (Mitte), but in the **outer residential rings**.
* **Top Priority:** **PLZ 12279 (Marienfelde)**.
    * **Population:** 16,381
    * **Stations:** 1
    * **Interpretation:** Over 16,000 residents are competing for a single public charging point.
* **Secondary Priority:** **PLZ 12309 (Lichtenrade)**.
    * **Population:** 15,900
    * **Stations:** 1
    * **Interpretation:** Extremely high pressure on grid; urgent need for expansion.

### **B. Geospatial Patterns**
* **The "Donut" Effect:** The map displays a ring of red areas (high population) surrounding the city center that often correspond to areas with lighter colors in the "Charging Station" layer, indicating a gap in supply.