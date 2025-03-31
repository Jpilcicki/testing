import pandas as pd
import numpy as np
import holoviews as hv
import panel as pn
import hvplot.pandas  # Required for pandas plotting interface
from bokeh.models import HoverTool
import warnings

# Filter out the specific FutureWarning from pandas
warnings.filterwarnings('ignore', category=FutureWarning, 
                       message='unique with argument that is not not a Series')

# Initialize Panel and HoloViews extensions
hv.extension('bokeh')
pn.extension()

# Read the dataset
df = pd.read_csv('sample_dataset.csv')

# Create age bands (5-year intervals)
df['AGE_BAND'] = pd.cut(df['AGE'], 
                    bins=range(0, 105, 5),
                    labels=[f'{i}-{i+4}' for i in range(0, 100, 5)],
                    right=False)

def create_heatmap(data, selected_classification=None, selected_age_band=None):
    """Create an interactive heatmap with optional filters"""
    # Filter data based on selections
    filtered_df = data.copy()
    if selected_classification is not None:
        filtered_df = filtered_df[filtered_df['CLASSIFICATION'] == selected_classification]
    if selected_age_band is not None:
        filtered_df = filtered_df[filtered_df['AGE_BAND'] == selected_age_band]
    
    # Create pivot table and format percentages
    pivot_data = pd.crosstab(filtered_df['CLASSIFICATION'], 
                            filtered_df['AGE_BAND'], 
                            normalize='index') * 100  # Convert to percentages
    
    # Format the hover tool to show percentages
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
        cmap='YlOrRd',
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

# Create interactive elements with lists
# Convert to numpy arrays first to avoid the pandas warning
classification_array = df['CLASSIFICATION'].to_numpy()
age_band_array = df['AGE_BAND'].to_numpy()

classification_values = ['All'] + sorted(np.unique(classification_array).astype(str).tolist())
age_band_values = ['All'] + sorted(np.unique(age_band_array).astype(str).tolist())

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

def update_dashboard(classification, age_band):
    """Update dashboard based on selections"""
    selected_class = None if classification == 'All' else int(classification)
    selected_age = None if age_band == 'All' else age_band
    
    heatmap = create_heatmap(df, selected_class, selected_age)
    
    # Create a container for the heatmap with specific dimensions
    return pn.Column(
        heatmap,
        width=800,
        height=300,  # Extra space for title and labels
        margin=(0, 0, 20, 0),  # top, right, bottom, left margins
        sizing_mode='fixed'    # Explicitly set sizing mode
    )

# Create the interactive dashboard with better spacing
dashboard = pn.Column(
    pn.pane.Markdown('# Interactive Classification Dashboard'),
    pn.Spacer(height=10),
    pn.Row(
        classification_selector, 
        pn.Spacer(width=20),
        age_band_selector,
        align='center'
    ),
    pn.Spacer(height=20),
    pn.bind(update_dashboard, classification_selector, age_band_selector),
    width=1000,
    height=600,  # Add explicit height
    margin=(20, 20, 20, 20),  # Add margin around the entire dashboard
    sizing_mode='fixed'       # Explicitly set sizing mode
)

# Serve the dashboard
if __name__ == '__main__':
    dashboard.show() 