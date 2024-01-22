from PIL import Image

def main_resize(image, short_size_in_pixels):
    if image is None:
        print('Image not found or cannot be loaded.')
    else:
        # Get the original resolution
        original_height = image.width
        original_width = image.height
        print(f'Original Resolution: {original_width}x{original_height}')

        # Determine the target short side length
        target_short_side = short_size_in_pixels

        # Calculate the new dimensions while preserving the aspect ratio
        if original_width < original_height:
            new_width = target_short_side
            new_height = int(original_height * (target_short_side / original_width))
        else:
            new_height = target_short_side
            new_width = int(original_width * (target_short_side / original_height))

        # Resize the image
        resized_image = image.resize((new_height, new_width))
        print(f'New Resolution: {new_height}x{new_width}')

        #Return the resized image (optional)
        return(resized_image)

if __name__ == "__main__":
    image = imread('test4.jpg')
    img = main_resize(image , 700)
    img.show()

