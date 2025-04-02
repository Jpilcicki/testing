import pandas as pd
import numpy as np
import holoviews as hv
import panel as pn
import hvplot.pandas  # Required for pandas plotting interface
from bokeh.models import HoverTool, TapTool
import warnings
import geopandas as gpd
import matplotlib.pyplot as plt
import geoviews as gv
from holoviews.streams import Selection1D, Tap

# Filter out the specific FutureWarning from pandas
warnings.filterwarnings('ignore', category=FutureWarning, 
                       message='unique with argument that is not not a Series')

# Initialize Panel and HoloViews extensions
hv.extension('bokeh')
gv.extension('bokeh')
pn.extension(design='material')  # Use material design for better styling

# Read the dataset
df = pd.read_csv('sample_dataset.csv')

# Create age bands (5-year intervals)
df['AGE_BAND'] = pd.cut(df['AGE'], 
                    bins=range(0, 105, 5),
                    labels=[f'{i}-{i+4}' for i in range(0, 100, 5)],
                    right=False)

# Global variable to store selected county
selected_county = None

@pn.cache
def get_filtered_data(data, selected_classification=None, selected_age_band=None, selected_county=None):
    """Get filtered dataset based on global filters"""
    filtered_df = data.copy()
    
    if selected_classification != 'All':
        filtered_df = filtered_df[filtered_df['CLASSIFICATION'] == int(selected_classification)]
    if selected_age_band != 'All':
        filtered_df = filtered_df[filtered_df['AGE_BAND'] == selected_age_band]
    if selected_county != 'All':
        filtered_df = filtered_df[filtered_df['COUNTY'] == selected_county]
    
    return filtered_df

def create_stats_box(filtered_df):
    """Create a statistics box showing counts and percentages"""
    # Calculate statistics
    total_count = len(filtered_df)
    ones_count = len(filtered_df[filtered_df['CLASSIFICATION'] == 1])
    ones_percentage = (ones_count / total_count * 100) if total_count > 0 else 0
    
    # Create the stats box
    stats_box = pn.Column(
        pn.pane.Markdown('### Classification Stats'),
        pn.pane.Markdown(f'**Total Class 1:** {ones_count:,}'),
        pn.pane.Markdown(f'**Class 1 Percentage:** {ones_percentage:.1f}%'),
        width=200,
        height=200,
        styles={'background': 'white',
                'border': '1px solid #ddd',
                'border-radius': '5px',
                'padding': '15px',
                'box-shadow': '2px 2px 5px rgba(0,0,0,0.1)'},
        margin=(0, 20, 0, 0),  # top, right, bottom, left
        sizing_mode='fixed'
    )
    
    return stats_box

def create_heatmap(filtered_df):
    """Create an interactive heatmap"""
    # Create pivot table and format percentages
    pivot_data = pd.crosstab(filtered_df['CLASSIFICATION'], 
                            filtered_df['AGE_BAND'], 
                            normalize='index') * 100  # Convert to percentages
    
    # Format the hover tool
    hover = HoverTool(
        tooltips=[
            ('Percentage', '@value{0.1f}%')
        ]
    )
    
    # Create interactive heatmap
    heatmap = pivot_data.hvplot.heatmap(
        title='Distribution of Classifications Across Age Bands',
        xlabel='',  # Remove x-label since we'll show it at top
        ylabel='Classification',
        cmap='BuPu',  # Changed from 'YlOrRd' to 'BuPu'
        height=200,
        width=800,
        colorbar=True,
        rot=45,
        clabel='Percentage',
        ylim=(-0.5, 1.5),  # Force y-axis to show just 0 and 1
        hover_cols=['value']  # Only show value in hover tooltip
    ).opts(
        tools=[hover],
        fontsize={
            'title': 16,
            'labels': 12,
            'xticks': 10,
            'yticks': 12
        },
        padding=0.1,
        show_grid=True,
        invert_yaxis=True,  # Put 0 at top
        xaxis='top',  # Move x-axis to top
        yticks=[0, 1]  # Force y-axis to show only 0 and 1
    )
    
    return heatmap

def create_va_heatmap(filtered_df):
    """Create an interactive heatmap of Virginia counties"""
    # Only use VA data
    va_data = filtered_df[filtered_df['STATE'] == 'VA'].copy()
    
    # Count class 1s by county
    class_1_counts = va_data[va_data['CLASSIFICATION'] == 1].groupby(['COUNTY_CODE', 'COUNTY']).size().reset_index(name='CLASS_1_COUNT')
    total_counts = va_data.groupby(['COUNTY_CODE', 'COUNTY']).size().reset_index(name='TOTAL_COUNT')
    
    # Merge the counts
    county_counts = pd.merge(class_1_counts, total_counts, on=['COUNTY_CODE', 'COUNTY'], how='outer')
    county_counts = county_counts.fillna(0)
    
    # Calculate percentage
    county_counts['CLASS_1_PERCENT'] = (county_counts['CLASS_1_COUNT'] / county_counts['TOTAL_COUNT'] * 100).round(1)
    county_counts['COUNTY_CODE'] = county_counts['COUNTY_CODE'].astype(str)
    
    # Read the shapefile
    va_counties = gpd.read_file('tl_2024_us_county/tl_2024_us_county.shp')
    va_counties = va_counties[va_counties['STATEFP'] == '51'].copy()
    va_counties['GEOID'] = va_counties['GEOID'].astype(str)
    
    # Merge with our count data
    va_counties = va_counties.merge(
        county_counts,
        left_on='GEOID',
        right_on='COUNTY_CODE',
        how='left'
    )
    
    # Fill NaN values with 0
    va_counties['CLASS_1_COUNT'] = va_counties['CLASS_1_COUNT'].fillna(0)
    va_counties['CLASS_1_PERCENT'] = va_counties['CLASS_1_PERCENT'].fillna(0)
    va_counties['TOTAL_COUNT'] = va_counties['TOTAL_COUNT'].fillna(0)
    
    # Create the interactive map
    hover = HoverTool(tooltips=[
        ('County', '@NAME'),
        ('Class 1 Count', '@CLASS_1_COUNT{0,0}'),
        ('Total Count', '@TOTAL_COUNT{0,0}'),
        ('Class 1 Percentage', '@CLASS_1_PERCENT{0.1f}%')
    ])

    # Create the map plot
    va_map = va_counties.hvplot.polygons(
        geo=True,
        title='Virginia Classification Distribution by County',
        hover_cols=['NAME', 'CLASS_1_COUNT', 'TOTAL_COUNT', 'CLASS_1_PERCENT'],
        c='CLASS_1_PERCENT',  # Color by percentage
        cmap='Blues',  # Changed from 'YlOrRd' to 'Blues'
        clim=(0, 100),  # Set color scale from 0-100%
        height=400,
        width=800,
        colorbar=None,  # Remove the legend
        line_color='black',  # Add county borders
        line_width=0.5,
        tools=['tap', hover, 'pan', 'wheel_zoom', 'reset']
    ).opts(
        active_tools=['pan'],
        bgcolor='white',  # White background
        show_frame=False,  # Remove frame
        fontsize={
            'title': 16,
            'labels': 12,
            'xticks': 10,
            'yticks': 12
        },
        padding=0.1,
        show_legend=False  # Ensure no legend is shown
    )
    
    return va_map

def update_dashboard(classification, age_band, county):
    """Update dashboard based on selections"""
    # Get filtered dataset
    filtered_df = get_filtered_data(df, classification, age_band, county)
    
    # Create all visualizations using the same filtered dataset
    heatmap = create_heatmap(filtered_df)
    stats_box = create_stats_box(filtered_df)
    va_map = create_va_heatmap(filtered_df)
    
    # Create a row with stats box and heatmap
    viz_row = pn.Column(
        pn.Row(
            stats_box,
            pn.Column(
                heatmap,
                width=800,
                height=300,
                margin=(0, 0, 20, 0),
                sizing_mode='fixed'
            ),
            sizing_mode='fixed',
            height=300,
            width=1000
        ),
        pn.Spacer(height=20),
        pn.Row(
            va_map,
            sizing_mode='fixed',
            height=400,
            width=1000
        ),
        sizing_mode='fixed'
    )
    
    return viz_row

# Create interactive elements with lists
classification_array = df['CLASSIFICATION'].to_numpy()
age_band_array = df['AGE_BAND'].to_numpy()
county_array = df[df['STATE'] == 'VA']['COUNTY'].to_numpy()

classification_values = ['All'] + sorted(np.unique(classification_array).astype(str).tolist())
age_band_values = ['All'] + sorted(np.unique(age_band_array).astype(str).tolist())
county_values = ['All'] + sorted(np.unique(county_array).astype(str).tolist())

classification_selector = pn.widgets.Select(
    name='Classification',
    options=classification_values,
    value='All',
    width=200
)

age_band_selector = pn.widgets.Select(
    name='Age Band',
    options=age_band_values,
    value='All',
    width=200
)

county_selector = pn.widgets.Select(
    name='County',
    options=county_values,
    value='All',
    width=200
)

# Add reset button
def reset_filters(event):
    classification_selector.value = 'All'
    age_band_selector.value = 'All'
    county_selector.value = 'All'

reset_button = pn.widgets.Button(
    name='Reset All Filters',
    button_type='warning',
    width=200
)
reset_button.on_click(reset_filters)

# Create the interactive dashboard
dashboard = pn.Column(
    pn.pane.Markdown('# Interactive Classification Dashboard'),
    pn.Spacer(height=10),
    pn.Row(
        classification_selector, 
        pn.Spacer(width=20),
        age_band_selector,
        pn.Spacer(width=20),
        county_selector,
        pn.Spacer(width=20),
        reset_button,
        align='center'
    ),
    pn.Spacer(height=20),
    pn.bind(update_dashboard, classification_selector, age_band_selector, county_selector),
    width=1000,
    height=800,
    margin=(20, 20, 20, 20),
    sizing_mode='fixed'
)

# Serve the dashboard
if __name__ == '__main__':
    dashboard.show() 
