import pandas as pd
import numpy as np
import geopandas as gpd
import panel as pn
import holoviews as hv
import geoviews as gv
import hvplot.pandas
from bokeh.models import HoverTool
import bokeh
import matplotlib.pyplot as plt
import warnings
import sys

# Print versions for debugging
print(f"Python version: {sys.version}")
print(f"pandas version: {pd.__version__}")
print(f"numpy version: {np.__version__}")
print(f"geopandas version: {gpd.__version__}")
print(f"panel version: {pn.__version__}")
print(f"holoviews version: {hv.__version__}")
print(f"geoviews version: {gv.__version__}")
print(f"bokeh version: {bokeh.__version__}")
print(f"matplotlib version: {plt.matplotlib.__version__}")
print("\n")

# Initialize extensions
hv.extension('bokeh')
gv.extension('bokeh')
pn.extension(design='material')

# Filter warnings
warnings.filterwarnings('ignore', category=FutureWarning)

# Create a simple test GeoDataFrame
# Using simple polygons data - a basic example that works with most GeoViews versions
def create_test_geodataframe():
    # Create a simple GeoDataFrame with polygons and value column
    from shapely.geometry import Polygon
    
    # Create 5 simple polygons
    geometries = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
        Polygon([(1, 1), (2, 1), (2, 2), (1, 2)]),
        Polygon([(2, 0), (3, 0), (3, 1), (2, 1)])
    ]
    
    # Create a GeoDataFrame with values
    data = {
        'id': range(1, 6),
        'value': [10, 30, 50, 70, 90],
        'name': [f'Region {i}' for i in range(1, 6)],
        'geometry': geometries
    }
    
    gdf = gpd.GeoDataFrame(data)
    return gdf

# Create the test GeoDataFrame
test_gdf = create_test_geodataframe()
print("Created test GeoDataFrame with columns:", test_gdf.columns.tolist())
print(test_gdf.head())
print("\n")

# Create a dashboard with multiple approaches to test compatibility
def create_compatibility_test():
    # ======== TEST 1: Basic approach with c parameter ========
    print("Creating Test 1: Basic approach with c parameter")
    try:
        test1 = test_gdf.hvplot.polygons(
            geo=True,
            c='value',
            cmap='Blues',
            title='Test 1: Basic approach with c parameter',
            height=300,
            width=400
        )
        print("✓ Test 1 created successfully\n")
    except Exception as e:
        print(f"✗ Test 1 failed: {str(e)}\n")
        test1 = pn.pane.Markdown(f"**Test 1 failed**: {str(e)}")
    
    # ======== TEST 2: Using color parameter with column name ========
    print("Creating Test 2: Using color parameter with column name")
    try:
        test2 = test_gdf.hvplot.polygons(
            geo=True,
            color='value',  # Using color parameter instead of c
            cmap='Blues',
            title='Test 2: Using color parameter with column name',
            height=300,
            width=400
        )
        print("✓ Test 2 created successfully\n")
    except Exception as e:
        print(f"✗ Test 2 failed: {str(e)}\n")
        test2 = pn.pane.Markdown(f"**Test 2 failed**: {str(e)}")
    
    # ======== TEST 3: Pre-computing colors as named colors ========
    print("Creating Test 3: Pre-computing colors as named colors")
    try:
        # Make a copy to avoid modifying the original
        test_gdf_with_colors = test_gdf.copy()
        
        # Map to plain named colors to avoid hex formats
        color_map = {
            10: 'lightblue',
            30: 'skyblue', 
            50: 'royalblue',
            70: 'darkblue',
            90: 'navy'
        }
        
        # Apply the color mapping function to create a new color column
        test_gdf_with_colors['fill_color'] = test_gdf_with_colors['value'].map(color_map)
        
        test3 = test_gdf_with_colors.hvplot.polygons(
            geo=True,
            color='fill_color',  # Use pre-computed color column
            title='Test 3: Pre-computing colors as named colors',
            height=300,
            width=400
        )
        print("✓ Test 3 created successfully\n")
    except Exception as e:
        print(f"✗ Test 3 failed: {str(e)}\n")
        test3 = pn.pane.Markdown(f"**Test 3 failed**: {str(e)}")
    
    # ======== TEST 4: Using fixed color ========
    print("Creating Test 4: Using fixed color")
    try:
        test4 = test_gdf.hvplot.polygons(
            geo=True,
            color='blue',  # Fixed color string
            title='Test 4: Using fixed color',
            height=300,
            width=400
        )
        print("✓ Test 4 created successfully\n")
    except Exception as e:
        print(f"✗ Test 4 failed: {str(e)}\n")
        test4 = pn.pane.Markdown(f"**Test 4 failed**: {str(e)}")
    
    # Create layout with all tests
    compatibility_dashboard = pn.Column(
        pn.pane.Markdown('# GeoViews Compatibility Test Dashboard'),
        pn.pane.Markdown('## Testing different polygon coloring methods'),
        pn.Row(
            pn.Column(test1, title='Test 1: c parameter'),
            pn.Column(test2, title='Test 2: color parameter')
        ),
        pn.Row(
            pn.Column(test3, title='Test 3: Pre-computed colors'),
            pn.Column(test4, title='Test 4: Fixed color')
        ),
        pn.pane.Markdown("""
        ## Compatibility Notes
        
        If you're seeing errors in the dashboard above, it indicates compatibility issues 
        between your environment versions:
        
        1. **Test 1 & 2**: If these fail but Test 3 works, you need to pre-compute colors
        2. **Test 3**: If this works, use the pre-computed color approach in your dashboard
        3. **Test 4**: If only this works, use fixed colors or consider matplotlib for rendering
        
        Based on which tests succeed, adapt your dashboard code to use the compatible method.
        """)
    )
    
    return compatibility_dashboard

# Create the compatibility dashboard
compatibility_dashboard = create_compatibility_test()

# Serve the dashboard
if __name__ == '__main__':
    compatibility_dashboard.show() 
