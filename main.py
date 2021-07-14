import mss
import cv2
import numpy as np

sct = mss.mss()

# Constants
# Threshold
BLUESTACKS_THRESHOLD = .90
# Box Drawing
BOX_COLOR = (0, 255, 0)
BOX_BORDER_WIDTH = 2

# Target Imgs
bluestacks_logo_img = cv2.imread('assets/bluestacks.png')
bluestacks_size_img = cv2.imread('assets/bluestacks_size.png')

# Get monitor screen
def get_monitor_scr():
    """Return the screenshot of the primary monitor.

    @returns Image with the screenshot.
    """
    img = np.array(sct.grab(sct.monitors[1]))
    return img[:,:,:3]

# Match and image with another
def match_image(compare_img, target_img):
    """Return the min max value and location of the matched image.

    @param compare_img Image where the search is running. It must be 8-bit or 32-bit floating-point..
    @param target_img Searched image. It must be not greater than the source image.

    @returns [min_val, max_val, min_loc, max_loc]
    """
    match = cv2.matchTemplate(compare_img, target_img, cv2.TM_CCOEFF_NORMED)
    return cv2.minMaxLoc(match)

# Get image dimensions (width and height)
def get_img_dimension(image):
    """Return given image x and y dimensions.

    @param image The image.

    @returns Tuple with x and y dimensions ([x, y]).
    """
    return [image.shape[1], image.shape[0]]

# Check if accuracy is above threshold
def is_accuracy_above_threshold(accuracy, threshold):
    """Check if the accuracy is above or equal the given threshold.

    @param accuracy The accuracy to test.
    @param threshold The threshold to test.

    @returns True if accuracy above or equal threshold and False if not.
    """
    return accuracy >= threshold

# Print a portion of the monitor
def get_monitor_segment_img(dimensions):
    """Return the image of a portion of the screen

    @param dimensions The dimensions of the portion of the screen.

    @returns The image with the portion of the screen.
    """
    return np.array(sct.grab(dimensions))

# Open a windows with the image
def open_image(title, image):
    """Open a window with the given title with the given image.

    @param title Window title.
    @param image The image.
    """
    cv2.imshow(title, image)
    cv2.waitKey()
    cv2.destroyAllWindows()

# Check if the BlueStacks window is maximized
def is_bluestacks_maximized(bluestacks_xloc):
    """Check if the BlueStacks window is maximized.

    @param bluestacks_xloc The top left position of bluestacks.

    @returns True if maximized and False if not.
    """
    return bluestacks_xloc < 10

# Draw rectangle in image
def draw_rect(image, start_vertex, end_vertex, rect_border_width):
    """Drawn an rectangle on the given image on the given location.

    @param image The image.
    @param start_vertex Initial vertex of the rectangle.
    @param end_vertex Ending vertex of the rectangle.
    @param color The color in (0, 255, 255) format.
    @param rect_border_width Size of the rect border in pixels.
    """
    cv2.rectangle(image, start_vertex, end_vertex, rect_border_width)


# Script Start
monitor_img = get_monitor_scr()

# Match bluestacks windows
bluestacks_min_val, bluestacks_max_val, bluestacks_min_loc, bluestacks_max_loc = match_image(
    monitor_img, bluestacks_logo_img)

print('Accuracy of BlueStacks window: %.2f%%' % bluestacks_max_val)

# Get bluestacks window dimensions
bluestacks_w, bluestacks_h = get_img_dimension(bluestacks_size_img)

if is_accuracy_above_threshold(bluestacks_max_val, BLUESTACKS_THRESHOLD):
    if is_bluestacks_maximized(bluestacks_max_loc[0]):
        # Get entire monitor image
        image_to_match = monitor_img
    else:
        # Get dimesion of bluestacks window
        dimensions_bluestacks = {
            'left': bluestacks_max_loc[0],
            'top': bluestacks_max_loc[1],
            'width': bluestacks_w,
            'height': bluestacks_h
        }

        image_to_match = get_monitor_segment_img(dimensions_bluestacks)

    open_image('Image to Match', image_to_match)
else:
    print('BlueStacks window not found. Check if the program is open, not minimized and in your primary monitor')
