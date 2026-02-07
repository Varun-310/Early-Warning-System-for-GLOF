import os
import numpy as np
import cv2  
import rasterio
import matplotlib.pyplot as plt
from skimage.restoration import denoise_bilateral # type: ignore
from sklearn.preprocessing import StandardScaler # type: ignore


def read_sar_image(image_path):
    
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  
    if image is None:
        raise ValueError(f"Error reading the image {image_path}")
    return image


def speckle_filter(image):

    filtered_image = denoise_bilateral(image, sigma_color=0.05, sigma_spatial=15)
    return filtered_image


def dn_to_sigma0(dn_image):
    # Replace zeros and negatives with a small positive value
    dn_image = np.where(dn_image > 0, dn_image, 1e-10)
    sigma0 = 10 * np.log10(dn_image)
    return sigma0

def clean_image(image):
    # Replace infinities or NaNs with the mean of valid values
    finite_mask = np.isfinite(image)
    mean_value = np.mean(image[finite_mask])
    image[~finite_mask] = mean_value
    return image

def normalize_image(image):
    # Standardize the image data: mean = 0, std = 1
    scaler = StandardScaler()
    image = scaler.fit_transform(image)
    return image


def display_image(image, title="Image"):
    plt.imshow(image, cmap='gray')
    plt.title(title)
    plt.colorbar()
    plt.show()


def save_image(image, output_path):
    
    cv2.imwrite(output_path, image)


def process_images_in_folder(input_folder, output_folder):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        
        if file_path.endswith(".jpg"):
            print(f"Processing: {filename}")
            sar_image = read_sar_image(file_path)
            filtered_image = speckle_filter(sar_image)
            sigma0_image = dn_to_sigma0(filtered_image)
            cleaned_image = clean_image(sigma0_image)
            normalized_image = normalize_image(cleaned_image)

            
            output_path = os.path.join(output_folder, f"preprocessed_{filename}")
            save_image(normalized_image, output_path)
            print(f"Saved preprocessed image to: {output_path}")

# Define the input and output folder paths for Pre-GLOF, During GLOF, and Post-GLOF
input_folder_pre_glof = 'data/Pre-glof'  
input_folder_during_glof = 'data/during-glof' 
input_folder_post_glof = 'data/post-glof'  
output_folder_pre_glof = 'data/processed_pre-glof'  
output_folder_during_glof = 'data/processed_during-glof'  
output_folder_post_glof = 'data/processed_post-glof'  

# Process all images for each folder
print("Processing Pre-GLOF images...")
#process_images_in_folder(input_folder_pre_glof, output_folder_pre_glof)

print("Processing During GLOF images...")
process_images_in_folder(input_folder_during_glof, output_folder_during_glof)

print("Processing Post-GLOF images...")
process_images_in_folder(input_folder_post_glof, output_folder_post_glof)