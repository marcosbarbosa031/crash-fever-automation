import os
import platform
import keyboard
import mss
import cv2
import win32api
import win32gui
import win32con
import numpy as np
import argparse
from time import time
from enum import Enum

sct = mss.mss()

# Constants
fps_time = time()
emulator_window = None

# Threshold
AUTO_THRESHOLD = .80
OK_THRESHOLD = .75
CONTINUE_THRESHOLD = .80
RETRY_THRESHOLD = .80
SKIP_THRESHOLD = .80
UPDATE_LIST_THRESHOLD = .99

# Box Drawing
BOX_COLOR = (0, 255, 0)
BOX_BORDER_WIDTH = 2

# Target Images
auto_btn_img = cv2.imread('assets/auto_btn_jpn.png')
ok_btn_img = cv2.imread('assets/ok_btn.png')
continue_btn_img = cv2.imread('assets/continue_btn_jpn.png')
retry_btn_img = cv2.imread('assets/retry_btn_jpn.png')
# skip_btn_img = cv2.imread('assets/skip_btn.png')
# update_list_btn_img = cv2.imread('assets/update_list_btn.png')

# Game state
class GAME_STATES(Enum):
    BOT_STARTED = None
    CLICKED_AUTO = { 'name': 'Auto Button', 'img': auto_btn_img, 'threshold': AUTO_THRESHOLD }
    CLICKED_OK = { 'name': 'Ok Button', 'img': ok_btn_img, 'threshold': OK_THRESHOLD }
    CLICKED_CONTINUE = { 'name': 'Continue Button', 'img': continue_btn_img, 'threshold': CONTINUE_THRESHOLD }
    CLICKED_RETRY = { 'name': 'Retry Button', 'img': retry_btn_img, 'threshold': RETRY_THRESHOLD }
    # CLICKED_SKIP = { 'name': 'Skip Button', 'img': skip_btn_img, 'threshold': SKIP_THRESHOLD }
    # CLICKED_UPDATE_LIST = { 'name': 'Update List Button', 'img': update_list_btn_img, 'threshold': UPDATE_LIST_THRESHOLD }

game_state = GAME_STATES.BOT_STARTED


# Get Window by name
def get_window(window_name):
    global emulator_window
    hWnd = win32gui.FindWindow(None, window_name)
    emulator_window = win32gui.FindWindowEx(hWnd, None, None, None)

# Get window dimensions
def get_window_dimensions(window):
    rect = win32gui.GetWindowRect(window)
    return [rect[0], rect[1], (rect[2] - rect[0]), (rect[3] - rect[1])]

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
    img = np.array(sct.grab(dimensions))
    img = img[:,:,:3]
    return img.copy()

# Open a windows with the image
def open_image(title, image):
    """Open a window with the given title with the given image.

    @param title Window title.
    @param image The image.
    """
    cv2.imshow(title, image)
    cv2.waitKey(1)

# Draw rectangle in image
def draw_rect(image, start_vertex, end_vertex, rect_color, rect_border_width):
    """Drawn a rectangle on the image on a specific location.

    @param image The image.
    @param start_vertex Initial vertex of the rectangle.
    @param end_vertex Ending vertex of the rectangle.
    @param color The color in (0, 255, 255) format.
    @param rect_border_width Size of the rect border in pixels.
    """
    cv2.rectangle(image, start_vertex, end_vertex, rect_color, rect_border_width)

# Click the image found on scree
def click_img_on_window(img, img_loc):
    """Click on the image found on window

    @param img The image to click.
    @param img_loc Tuple with image x and y location.
    """
    w, h = get_img_dimension(img)
    draw_rect(emulator_img, img_loc, (img_loc[0] + w, img_loc[1] + h), BOX_COLOR, BOX_BORDER_WIDTH)

    x = img_loc[0] + (w//2)
    y = img_loc[1] + (h//2)

    lParam = win32api.MAKELONG(x, y)
    win32gui.SendMessage(emulator_window, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
    win32gui.SendMessage(emulator_window, win32con.WM_LBUTTONUP, None, lParam)

# Find image on the specific game state
def find_and_click_img(state):
    """Find image on the specific game state.

    @param state The game state with the image to find and threshold.
    """

    img = state.value['img']
    threshold = state.value['threshold']
    button_name = state.value['name']
    _, max_val, _, max_loc = match_image(emulator_img, img)

    print_accuracy_image(max_val, button_name)

    if is_accuracy_above_threshold(max_val, threshold):
        click_img_on_window(img, max_loc)
        update_state(state)
        # open_image('Crash Fever', emulator_img)

# Update game state
def update_state(state):
    global game_state
    game_state = state

# Print FPS
def print_fps():
    """Print FPS on console
    """
    # Clear screen based on OS
    clear_command = 'cls' if platform.system() == 'Windows' else 'clear'
    os.system(clear_command)
    try:
        print('FPS: %.0f' % (1 / (time() - fps_time)))
    except:
        None
        None
    fps_time = time()

# Print game state
def print_game_state():
    """Print game state on console
    """
    print("Game State:", game_state.name)

# Print accuracy of image
def print_accuracy_image(accuracy, button_name):
    """Print accuracy of image
    """
    print("Accuracy of", button_name, ": %.2f%%" % (accuracy*100))

# Get emulator windows image
def get_emulator_window_img():
    x, y, w, h = get_window_dimensions(emulator_window)
    dimensions = { 'left': x, 'top': y, 'width': w, 'height': h }
    return get_monitor_segment_img(dimensions)

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Bot for automating game actions')
    parser.add_argument('--app_name', type=str, default='BlueStacks',
                        help='Name of the application window to control (default: BlueStacks)')
    return parser.parse_args()

# Script Start
if __name__ == "__main__":
    args = parse_args()
    get_window(args.app_name)

while True:
    print_fps()
    print_game_state()

    emulator_img = get_emulator_window_img()

    for state in GAME_STATES:
        if state.value is not None:
            find_and_click_img(state)

    # open_image('Crash Fever', emulator_img)

    # if keyboard.is_pressed('c'):
    #     break
