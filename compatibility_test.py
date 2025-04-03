import pandas as pd
import numpy as np
import geopandas as gpd
import panel as pn
import holoviews as hv
import geoviews as gv
import hvplot.pandas
from bokeh.models import HoverTool
from bokeh.transform import linear_cmap
from bokeh.palettes import Blues9
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
print(f"bokeh version: {hv.extension.bokeh.__version__}")
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
    
    # Define a blue color palette
    blue_palette = Blues9
    
    # ======== TEST 1: Basic approach with c parameter ========
    # This is the most common approach but can sometimes cause compatibility issues
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
    
    # ======== TEST 2: Using fill_color with linear_cmap ========
    # This uses Bokeh's transform system, which might work differently
    print("Creating Test 2: Using fill_color with linear_cmap")
    try:
        color_mapper = linear_cmap('value', palette=blue_palette, low=0, high=100)
        test2 = test_gdf.hvplot.polygons(
            geo=True,
            fill_color=color_mapper,
            title='Test 2: Using fill_color with linear_cmap',
            height=300,
            width=400
        )
        print("✓ Test 2 created successfully\n")
    except Exception as e:
        print(f"✗ Test 2 failed: {str(e)}\n")
        test2 = pn.pane.Markdown(f"**Test 2 failed**: {str(e)}")
    
    # ======== TEST 3: Pre-computing colors directly ========
    # Pre-compute colors in the DataFrame to avoid dynamic mapping
    print("Creating Test 3: Pre-computing colors directly")
    try:
        # Make a copy to avoid modifying the original
        test_gdf_with_colors = test_gdf.copy()
        
        # Define a function to map value to color
        def get_color_for_value(value):
            # Ensure value is within 0-100 range
            value = max(0, min(100, value))
            # Map to index in the palette
            idx = int(value / 100 * 8)  # 8 = len(blue_palette) - 1
            return blue_palette[8 - idx]  # Reverse index to get darker blue for higher values
        
        # Apply the color mapping function to create a new color column
        test_gdf_with_colors['color'] = test_gdf_with_colors['value'].apply(get_color_for_value)
        
        test3 = test_gdf_with_colors.hvplot.polygons(
            geo=True,
            color='color',  # Use pre-computed color column
            title='Test 3: Pre-computing colors directly',
            height=300,
            width=400
        )
        print("✓ Test 3 created successfully\n")
    except Exception as e:
        print(f"✗ Test 3 failed: {str(e)}\n")
        test3 = pn.pane.Markdown(f"**Test 3 failed**: {str(e)}")
    
    # ======== TEST 4: Using geoviews directly ========
    # Try using GeoViews directly instead of hvplot
    print("Creating Test 4: Using geoviews directly")
    try:
        # Create a colormapper for the values
        from holoviews.operation.datashader import rasterize
        from holoviews import opts
        
        # Convert GeoDataFrame to a GeoViews Polygons object
        polygons = gv.Polygons(test_gdf, vdims=['value', 'name'])
        
        # Apply colormapping and style
        test4 = polygons.opts(
            opts.Polygons(
                color='value', 
                colorbar=True, 
                cmap='Blues',
                tools=['hover'],
                height=300, 
                width=400,
                title='Test 4: Using geoviews directly'
            )
        )
        print("✓ Test 4 created successfully\n")
    except Exception as e:
        print(f"✗ Test 4 failed: {str(e)}\n")
        test4 = pn.pane.Markdown(f"**Test 4 failed**: {str(e)}")
    
    # ======== TEST 5: Using fixed colors ========
    # Use a fixed color for all polygons as a fallback
    print("Creating Test 5: Using fixed colors")
    try:
        test5 = test_gdf.hvplot.polygons(
            geo=True,
            color='blue',  # Fixed color string
            title='Test 5: Using fixed colors',
            height=300,
            width=400
        )
        print("✓ Test 5 created successfully\n")
    except Exception as e:
        print(f"✗ Test 5 failed: {str(e)}\n")
        test5 = pn.pane.Markdown(f"**Test 5 failed**: {str(e)}")

    # ======== TEST 6: Using matplotlib backend ========
    # Try using matplotlib backend instead of bokeh
    print("Creating Test 6: Using matplotlib backend")
    try:
        # Save current backend and switch to matplotlib
        current_backend = hv.Store.current_backend
        hv.Store.current_backend = 'matplotlib'
        
        test6_raw = test_gdf.hvplot.polygons(
            c='value',
            cmap='Blues',
            title='Test 6: Using matplotlib backend',
            height=300,
            width=400
        )
        
        # Convert to static image for display in bokeh
        test6_png = hv.render(test6_raw)
        test6 = pn.pane.PNG(test6_png)
        
        # Restore backend
        hv.Store.current_backend = current_backend
        print("✓ Test 6 created successfully\n")
    except Exception as e:
        print(f"✗ Test 6 failed: {str(e)}\n")
        test6 = pn.pane.Markdown(f"**Test 6 failed**: {str(e)}")
    
    # Create layout with all tests
    compatibility_dashboard = pn.Column(
        pn.pane.Markdown('# GeoViews Compatibility Test Dashboard'),
        pn.pane.Markdown('## Testing different polygon coloring methods'),
        pn.Row(
            pn.Column(test1, title='Test 1: Basic approach'),
            pn.Column(test2, title='Test 2: Using linear_cmap'),
            pn.Column(test3, title='Test 3: Pre-computed colors'),
        ),
        pn.Row(
            pn.Column(test4, title='Test 4: GeoViews direct'),
            pn.Column(test5, title='Test 5: Fixed colors'),
            pn.Column(test6, title='Test 6: Matplotlib backend'),
        ),
        pn.pane.Markdown("""
        ## Compatibility Notes
        
        If you're seeing errors in the dashboard above, it indicates compatibility issues between 
        your local environment and deployment environment:
        
        1. **Version differences**: Different versions of HoloViews, GeoViews, Bokeh, or Panel 
           may handle parameters differently.
        2. **Coloring methods**: Different environments may require different approaches to coloring.
        3. **Rendering backends**: If Bokeh fails, you might need to use a different backend.
        
        Based on which tests succeed and which fail, you can adapt your dashboard code to use 
        the compatible method.
        """)
    )
    
    return compatibility_dashboard

# Create the compatibility dashboard
compatibility_dashboard = create_compatibility_test()

# Serve the dashboard
if __name__ == '__main__':
    compatibility_dashboard.show() 