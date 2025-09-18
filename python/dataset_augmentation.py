import os
import random
import cv2
import glob
import imutils
import numpy as np
from PIL import Image
from PIL.Image import Image as PILImage

from utils_ import numerical_sort  # Custom utility functions


def resize_to_pixels(image_path: str, pixels: int = 512) -> PILImage:
    """
    Resizes an image so that its smallest dimension becomes 512 pixels,
    maintaining aspect ratio for the other dimension.

    Parameters:
        image_path (str): Path to the input image.
    Returns:
        PIL.Image: The resized image.
    """
    with Image.open(image_path) as img:
        original_width, original_height = img.size

        # Calculate scale factor to make the smallest dimension 512
        scale_factor = pixels / min(original_width, original_height)

        # Calculate new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Resize and save
        resized_img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

        return resized_img


def crop_center(input_dir: str, output_dir: str) -> None:
    """
    Crops the center of each image from the input folder and optionally resizes it,
    saving the result into the specified output folder.

    Parameters:
        output_dir (str): Directory where cropped images will be saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop through all files in the folder
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')):
            filepath = os.path.join(input_dir, filename)

            resized_image = resize_to_pixels(filepath)
            width, height = resized_image.size

            # Square cropping
            crop_width, crop_height = (256 * 2), (256 * 2)

            # Compute center crop coordinates
            left = (width - crop_width) // 2
            upper = (height - crop_height) // 2
            right = min(left + crop_width, width)
            lower = min(upper + crop_height, height)

            # Skip if image is too small
            if (right - left) < crop_width or (lower - upper) < crop_height:
                print(f"Skipping {filename}: image too small for requested crop.")
                continue

            cropped_img = resized_image.crop((left, upper, right, lower))

            # Save output image as PNG
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.png")
            cropped_img.save(output_path, format="PNG")

    print("Cropping complete.")

    return None


def generate_augmented_images(dataset_output_dir: str, source_image_path: str, phase: str,
                              std_min: float = 0, std_max: float = 0.3,
                              rot: str = 'OFF', blur_min: int = 1, blur_max: int = 4):
    """
    Applies random noise, optional rotation, and blurring to an image to augment it.

    Parameters:
        dataset_output_dir (str): Base directory to save augmented images.
        source_image_path (str): Path to the reference image.
        std_min (float): Min standard deviation for Gaussian noise.
        std_max (float): Max standard deviation for Gaussian noise.
        rot (str): 'ON' to apply rotations, 'OFF' otherwise.
        blur_min (int): Starting kernel size for blurring.
        blur_max (int): Ending kernel size for blurring.
        phase (str): Either 'Enrollment' or 'Authentication'.
    """
    n_attempts = 20 if 'Authentication' in phase else 1
    image_name = source_image_path.strip('/').split('/')[-1][:-4]
    IMAGE_ = cv2.imread(source_image_path)
    h, w, d = IMAGE_.shape

    for i in range(1, n_attempts + 1):
        augmented_set_dir = os.path.join(dataset_output_dir, image_name, f'F_{i}')
        os.makedirs(augmented_set_dir, exist_ok=True)
        counter = 7

        if rot == 'OFF':
            # Noise and blur variations
            for val in np.random.uniform(std_min, std_max, 6):
                gauss_noise = np.random.normal(0, val, IMAGE_.size).reshape(h, w, d).astype('uint8')
                img_gauss = cv2.add(IMAGE_, gauss_noise)
                for blur in range(blur_min, blur_max):
                    if counter <= 0: break
                    counter -= 1
                    image_blurred = cv2.blur(img_gauss, (blur, blur))
                    filename = f"{image_name}_gauss_{round(val, 5):.5f}".replace('.', '_') + f"_blur_{blur}.png"
                    cv2.imwrite(os.path.join(augmented_set_dir, filename), image_blurred)
        else:
            # Rotation, noise, and blur
            cv2.imwrite(os.path.join(augmented_set_dir, f"{image_name}.png"), IMAGE_)
            rot_start, rot_stop = 1, 6
            for angle in random.sample(range(rot_start, rot_stop), (rot_stop - rot_start)):
                val = random.uniform(std_min, std_max)
                gauss_noise = np.random.normal(0, val, IMAGE_.size).reshape(h, w, d).astype('uint8')
                img_gauss = cv2.add(IMAGE_, gauss_noise)
                image_rotated = imutils.rotate(img_gauss, angle)
                for blur in range(blur_min, blur_max):
                    if counter <= 0: break
                    counter -= 1
                    image_blurred = cv2.blur(image_rotated, (blur, blur))
                    filename = f"{image_name}_rot_{angle}_gauss_{round(val, 4):.4f}".replace('.',
                                                                                             '_') + f"_blur_{blur}.png"
                    cv2.imwrite(os.path.join(augmented_set_dir, filename), image_blurred)


def generate_augmented_dataset(processed_imgs_dir: str, output_database_dir: str, phases: str = "BOTH"):
    """
    Generates datasets by applying augmentation to images based on the given phase.

    Parameters:
        processed_imgs_dir (str): Directory with cropped and resized reference images.
        phases (str): 'BOTH' for Enrollment and Authentication, or 'Enrollment' only.
    """
    img_types = [f for f in os.listdir(processed_imgs_dir) if not f.startswith('.')]
    phases = ['Enrollment', 'Authentication'] if phases == "BOTH" else [phases]

    for type in img_types:
        for phase in phases:
            ref_images = sorted(glob.glob(os.path.join(processed_imgs_dir, type, '*.png')), key=numerical_sort)
            for ref_image in ref_images:
                if ref_image.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')):
                    generate_augmented_images(os.path.join(output_database_dir, phase, type), ref_image, phase=phase)

    return None


# Define base paths
base_path = '<ADD YOUR BASEPATH>'
raw_images_dir = os.path.join(base_path, 'raw')  # Raw images folder
processed_images_dir = os.path.join(base_path, 'processed/')  # Processed images folder
output_database_dir = os.path.join(base_path, 'csr_images/')  # Output folder for generated datasets

# Create the set images processed
crop_center(raw_images_dir, processed_images_dir)

# Start dataset augmentation
generate_augmented_dataset(processed_images_dir, output_database_dir, phases='BOTH')
