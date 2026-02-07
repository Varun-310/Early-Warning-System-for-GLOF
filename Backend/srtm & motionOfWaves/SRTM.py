import rasterio
import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import gaussian_filter
import streamlit as st
import time

# Streamlit app title
st.title("Interactive DEM Analysis: Water Flow, Submerged Areas, and Overflow Calculation")

# File uploader for DEM
st.sidebar.header("Upload and Settings")
dem_file = st.sidebar.file_uploader("Upload your DEM GeoTIFF file:", type=["tif", "tiff"])

# Inputs for customization
st.sidebar.subheader("Customization Options")
downscale_factor = st.sidebar.slider("Downscaling Factor (higher = more compression):", 1, 10, 5)
water_level_threshold_input = st.sidebar.slider("Water Level Threshold (% of elevation):", 1, 100, 90)
animation_speed = st.sidebar.slider("Animation Speed (seconds per frame):", 0.1, 5.0, 1.0)

# Animation controls
st.sidebar.subheader("Animation Controls")
animation_active = st.sidebar.checkbox("Start Animation", value=True)

if dem_file is not None:
    try:
        # Step 1: Load the DEM GeoTIFF file
        with rasterio.open(dem_file) as dem_file_obj:
            dem_data = dem_file_obj.read(1).astype(float)  # Convert to float to handle NaN
            dem_transform = dem_file_obj.transform
            dem_crs = dem_file_obj.crs
            dem_data[dem_data == dem_file_obj.nodata] = np.nan  # Handle NoData values

        # Step 2: Downsample the DEM
        dem_data = dem_data[::downscale_factor, ::downscale_factor]

        # Step 3: Apply Gaussian smoothing
        dem_smoothed = gaussian_filter(dem_data, sigma=2)

        # Step 4: Calculate water flow direction and slope
        gradient_y, gradient_x = np.gradient(-dem_smoothed)  # Negative for downhill flow
        flow_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)  # Slope magnitude
        flow_direction = np.degrees(np.arctan2(gradient_y, gradient_x))  # Flow direction (0-360 degrees)
        flow_direction = (flow_direction + 360) % 360  # Normalize to 0-360 degrees

        grad_x_normalized = gradient_x / (flow_magnitude + 1e-9)
        grad_y_normalized = gradient_y / (flow_magnitude + 1e-9)

        # Step 5: Calculate submerged areas based on water level
        water_level_threshold = np.nanpercentile(dem_smoothed, water_level_threshold_input)
        water_mask = dem_smoothed <= water_level_threshold
        submerged_volume = np.nansum(water_mask * (water_level_threshold - dem_smoothed))
        submerged_area = np.nansum(water_mask) * (downscale_factor**2)
        overflow_rate = np.nansum(flow_magnitude * water_mask)

        # Step 6: Prepare visualization data
        height, width = dem_data.shape
        x = np.linspace(0, width - 1, width)
        y = np.linspace(0, height - 1, height)
        x, y = np.meshgrid(x, y)

        chart_placeholder = st.empty()
        metrics_placeholder = st.empty()

        # Step 7: Animate flow directions
        step = max(1, downscale_factor * 2)  
        frames = 100  

        frame = 0  
        while animation_active:
            arrow_scale = 1 + 0.5 * np.sin(2 * np.pi * frame / frames)  

            fig = go.Figure()

            fig.add_trace(go.Surface(
                z=dem_data,
                x=x,
                y=y,
                colorscale=[[0, 'black'], [1, 'white']],
                colorbar_title='Elevation (m)',
                showscale=True,
                opacity=1,
                name="Elevation"
            ))

            submerged_colors = np.where(water_mask, dem_smoothed, np.nan)
            fig.add_trace(go.Surface(
                z=dem_data,  
                x=x,
                y=y,
                surfacecolor=submerged_colors,  
                colorscale='Blues',  
                showscale=True,
                opacity=0.7,
                name="Submerged Areas"
            ))

            fig.add_trace(go.Cone(
                x=x[::step, ::step].flatten(),
                y=y[::step, ::step].flatten(),
                z=dem_data[::step, ::step].flatten(),
                u=(arrow_scale * grad_x_normalized[::step, ::step]).flatten(),
                v=(arrow_scale * grad_y_normalized[::step, ::step]).flatten(),
                w=np.zeros_like(flow_magnitude[::step, ::step]).flatten(),  
                sizemode="absolute",
                sizeref=2,
                colorscale=[[0, 'red'], [1, 'red']],  
                showscale=False,
                name="Water Flow Direction"
            ))

            fig.update_layout(
                title="DEM Analysis: Water Flow & Submerged Areas",
                scene=dict(
                    xaxis_title='X Coordinate',
                    yaxis_title='Y Coordinate',
                    zaxis_title='Elevation (m)'
                ),
                margin=dict(l=0, r=0, t=50, b=0)
            )

            chart_placeholder.plotly_chart(fig, use_container_width=True)

            metrics_placeholder.markdown(
                f"""
                **Water Flow Metrics**  
                - **Submerged Volume**: {submerged_volume:.2f} m³  
                - **Submerged Area**: {submerged_area:.2f} m²  
                - **Water Level Threshold**: {water_level_threshold:.2f} m  
                - **Overflow Rate**: {overflow_rate:.2f} m³/s  
                - **Flow Velocity (Avg)**: {np.nanmean(flow_magnitude):.2f} m/s  
                - **Frame**: {frame + 1}/{frames}
                """
            )

            frame = (frame + 1) % frames
            time.sleep(animation_speed)

    except Exception as e:
        st.error(f"An error occurred: {e}")
