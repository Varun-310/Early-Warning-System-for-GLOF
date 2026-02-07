import os
import numpy as np
import cv2
from skimage.filters import threshold_otsu
from skimage.morphology import dilation, disk
from skimage import measure
import matplotlib.pyplot as plt
import pandas as pd  # For tabular summaries

# Function to process a single image
def process_glacial_image(image_path, resolution):
    # Validate image path
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Load the image
    image = cv2.imread(image_path)

    # Check if image is loaded successfully
    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use Otsu's thresholding for segmentation
    lake_threshold = threshold_otsu(gray)

    # Create binary masks
    lake_mask = gray <= lake_threshold
    ice_mask = gray > lake_threshold

    # Label the regions
    lake_labeled = measure.label(lake_mask)
    ice_labeled = measure.label(ice_mask)

    # Function to get the size of the largest region
    def get_largest_region_size(labeled_image):
        props = measure.regionprops(labeled_image)
        return max([prop.area for prop in props]) if props else 0

    # Get initial sizes
    lake_size_before = get_largest_region_size(lake_labeled)
    ice_size_before = get_largest_region_size(ice_labeled)

    # Convert pixel areas to square meters
    lake_size_before_m2 = lake_size_before * (resolution ** 2)
    ice_size_before_m2 = ice_size_before * (resolution ** 2)

    # Apply conservative dilation
    dilated_lake = dilation(lake_mask, disk(5))
    dilated_ice = dilation(ice_mask, disk(3))

    # Label the dilated regions
    lake_labeled_dilated = measure.label(dilated_lake)
    ice_labeled_dilated = measure.label(dilated_ice)

    # Get new sizes
    lake_size_after = get_largest_region_size(lake_labeled_dilated)
    ice_size_after = get_largest_region_size(ice_labeled_dilated)

    # Convert new sizes to square meters
    lake_size_after_m2 = lake_size_after * (resolution ** 2)
    ice_size_after_m2 = ice_size_after * (resolution ** 2)

    # Calculate percentage increases/decreases
    lake_change_percent = ((lake_size_after_m2 - lake_size_before_m2) / lake_size_before_m2) * 100 if lake_size_before_m2 > 0 else 0
    ice_change_percent = ((ice_size_after_m2 - ice_size_before_m2) / ice_size_before_m2) * 100 if ice_size_before_m2 > 0 else 0

    # Calculate total area and water percentage
    total_area_m2 = (image.shape[0] * image.shape[1]) * (resolution ** 2)
    water_percentage = (lake_size_after_m2 / total_area_m2) * 100 if total_area_m2 > 0 else 0

    ice_status = "No ice detected" if ice_size_after_m2 == 0 else f"{ice_size_after_m2:.2f} m²"


    return {
        'image': image,
        'lake_mask': lake_mask,
        'ice_mask': ice_mask,
        'lake_size_before_m2': lake_size_before_m2,
        'ice_size_before_m2': ice_size_before_m2,
        'lake_size_after_m2': lake_size_after_m2,
        'ice_size_after_m2': ice_size_after_m2,
        'lake_change_percent': lake_change_percent,
        'ice_change_percent': ice_change_percent,
        'total_area_m2': total_area_m2,
        'water_percentage': water_percentage,
        'ice_status': ice_status
    }


# Function to create visualizations for multiple images
def create_detailed_visualization(image_name, results):
    # Extract data
    image = results['image']
    lake_mask = results['lake_mask']
    ice_mask = results['ice_mask']
    lake_change_percent = results['lake_change_percent']
    ice_change_percent = results['ice_change_percent']
    water_percentage = results['water_percentage']
    total_area_m2 = results['total_area_m2']

    # Plot original image
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 3, 1)
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(f"Original: {image_name}")
    plt.axis('off')

    # Plot lake mask
    plt.subplot(1, 3, 2)
    plt.imshow(lake_mask, cmap='Blues')
    plt.title("Lake Mask")
    plt.axis('off')

    # Plot ice mask
    plt.subplot(1, 3, 3)
    plt.imshow(ice_mask, cmap='Greens')
    plt.title("Ice Mask")
    plt.axis('off')

    # Add text information
    plt.suptitle(
        f"Lake Change: {lake_change_percent:.2f}%, Ice Change: {ice_change_percent:.2f}%\n"
        f"Water Coverage: {water_percentage:.2f}%, Total Area: {total_area_m2:.2f} m²",
        fontsize=12
    )
    plt.tight_layout()
    plt.show()

    ice_status = results['ice_status']

    # Add text information
    plt.suptitle(
        f"Lake Change: {lake_change_percent:.2f}%, Ice Status: {ice_status}\n"
        f"Water Coverage: {water_percentage:.2f}%, Total Area: {total_area_m2:.2f} m²",
        fontsize=12
    )


# Function to process multiple images
def process_multiple_images(image_paths, resolution=10):
    """
    Process multiple glacial images and visualize detailed results.

    :param image_paths: List of image file paths
    :param resolution: Resolution in meters per pixel (default 10)
    :return: Dictionary of processing results
    """
    processing_results = {}

    for image_path in image_paths:
        try:
            # Extract just the filename for display
            image_name = os.path.basename(image_path)

            # Process the image
            result = process_glacial_image(image_path, resolution)

            # Store the result
            processing_results[image_name] = result

            # Create detailed visualization for each image
            create_detailed_visualization(image_name, result)

        except Exception as e:
            print(f"Error processing {image_path}: {e}")

    return processing_results


def create_comparison_graph_and_summary(results):
    """
    Create comparison graphs for lake and ice changes across all processed images
    and summarize the results in tabular format.

    :param results: Dictionary of processing results for all images
    """
    # Prepare data for visualization
    image_names = list(results.keys())
    lake_sizes_before = [res['lake_size_before_m2'] for res in results.values()]
    lake_sizes_after = [res['lake_size_after_m2'] for res in results.values()]
    ice_sizes_before = [res['ice_size_before_m2'] for res in results.values()]
    ice_sizes_after = [res['ice_size_after_m2'] for res in results.values()]
    lake_changes = [res['lake_change_percent'] for res in results.values()]
    ice_changes = [res['ice_change_percent'] for res in results.values()]
    water_percentages = [res['water_percentage'] for res in results.values()]
    total_areas = [res['total_area_m2'] for res in results.values()]
    ice_statuses = [res['ice_status'] for res in results.values()]

    # Create bar chart for lake and ice sizes
    x = np.arange(len(image_names))  # Index for images
    width = 0.35  # Bar width

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width / 2, lake_sizes_before, width, label='Lake Before (m²)', color='blue')
    ax.bar(x + width / 2, lake_sizes_after, width, label='Lake After (m²)', color='cyan')
    ax.bar(x - width / 2, ice_sizes_before, width, bottom=lake_sizes_before, label='Ice Before (m²)', color='green')
    ax.bar(x + width / 2, ice_sizes_after, width, bottom=lake_sizes_after, label='Ice After (m²)', color='lightgreen')

    # Add labels, legend, and title
    ax.set_xticks(x)
    ax.set_xticklabels(image_names, rotation=45, ha='right')
    ax.set_ylabel('Size (m²)')
    ax.set_title('Comparison of Lake and Ice Sizes Before and After Processing')
    ax.legend()

    plt.tight_layout()
    plt.show()

    # Tabular summary using pandas
    summary_table = pd.DataFrame({
        'Image': image_names,
        'Lake Size Before (m²)': lake_sizes_before,
        'Lake Size After (m²)': lake_sizes_after,
        'Lake Change (%)': lake_changes,
        'Ice Size Before (m²)': ice_sizes_before,
        'Ice Size After (m²)': ice_sizes_after,
        'Ice Change (%)': ice_changes,
        'Water Percentage (%)': water_percentages,
        'Total Area (m²)': total_areas,
        'Ice Status': ice_statuses,
    })

    print("\nSummary of Results:")
    print(summary_table.to_string(index=False))


# Example usage
if __name__ == "__main__":
    # List of image paths
    image_paths = [
        'images/satellite images2.png',
        'images/satellite images 3.png',
        'images/satellite image1.png',
        'images/pond1.jpg',
        'images/pond2.jpg',
        'images/southglacial1.png',
        'images/southglacial2.png',
        'images/southglacial3.png',
    ]

    # Process the images
    results = process_multiple_images(image_paths, resolution=10)

    # Create comparison graph and print the summary
    create_comparison_graph_and_summary(results)


    # Print a summary of results
    for image_name, result in results.items():
        print(f"Image: {image_name}")
        print(f"  Lake Size Before (m²): {result['lake_size_before_m2']:.2f}")
        print(f"  Lake Size After (m²): {result['lake_size_after_m2']:.2f}")
        print(f"  Lake Change (%): {result['lake_change_percent']:.2f}")
        print(f"  Ice Size Before (m²): {result['ice_size_before_m2']:.2f}")
        print(f"  Ice Size After (m²): {result['ice_size_after_m2']:.2f}")
        print(f"  Ice Change (%): {result['ice_change_percent']:.2f}")
        print(f"  Ice Status: {result['ice_status']}")
        print(f"  Total Area (m²): {result['total_area_m2']:.2f}")
        print(f"  Water Percentage (%): {result['water_percentage']:.2f}\n")
