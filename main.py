import os
import mss
import cv2
import keyboard
import pyautogui
import numpy as np
from enum import Enum
from time import time, sleep

sct = mss.mss()

# Constants
pyautogui.PAUSE = 0

# Threshold
BLUESTACKS_THRESHOLD = .90
AUTO_THRESHOLD = .80
OK_THRESHOLD = .80
CONTINUE_THRESHOLD = .80
RETRY_THRESHOLD = .80

# Box Drawing
BOX_COLOR = (0, 255, 0)
BOX_BORDER_WIDTH = 2

# Game state
class GAME_STATES(Enum):
    GAME_AUTO_OFF = 1
    GAME_END_MESSAGE = 2
    GAME_END_BONUS = 3
    GAME_QUEST_CLEAR = 4

game_state = GAME_STATES.GAME_AUTO_OFF
fps_time = time()

# Drawing
RECT_COLOR = (0, 255, 0)
RECT_BORDER_WIDTH = 2

# Target Images
auto_btn_img = cv2.imread('assets/auto_btn.png')
ok_btn_img = cv2.imread('assets/ok_btn.png')
continue_btn_img = cv2.imread('assets/continue_btn.png')
retry_btn_img = cv2.imread('assets/retry_btn.png')


# Get monitor screen
def get_monitor_scr():
    """Return the screenshot of the primary monitor.

    @returns Image with the screenshot.
    """
    img = np.array(sct.grab(sct.monitors[1]))
    img = img[:,:,:3]
    return img.copy()

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
    cv2.waitKey(1)

# Check if the BlueStacks window is maximized
def is_bluestacks_maximized(bluestacks_xloc):
    """Check if the BlueStacks window is maximized.

    @param bluestacks_xloc The top left position of bluestacks.

    @returns True if maximized and False if not.
    """
    return bluestacks_xloc < 10

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

# Go to next game state
def next_state():
    """Update game state to next state
    """
    global game_state
    next = game_state.value + 1 if game_state.value < len(GAME_STATES) else 1
    game_state = GAME_STATES(next)

# Click the image found on scree
def click_img_on_screen(img, img_loc):
    """Click on the image found on screen

    @param img The image to click.
    @param img_loc Tuple with image x and y location.
    """
    w, h = get_img_dimension(img)
    draw_rect(monitor_img, img_loc, (img_loc[0] + w, img_loc[1] + h), RECT_COLOR, RECT_BORDER_WIDTH)

    click_x = img_loc[0] + (w/2)
    click_y = img_loc[1] + (h/2)

    pyautogui.click(click_x, click_y)

# Find image on the specific game state
def find_and_click_img(img, threshold):
    """Find image on the specific game state.

    @param img The image to click.
    @param threshold image threshold.
    """
    global game_state, accuracy
    _, max_val, _, max_loc = match_image(monitor_img, img)
    accuracy = max_val

    if is_accuracy_above_threshold(accuracy, threshold):
        click_img_on_screen(img, max_loc)
        next_state()

# Print FPS
def print_fps():
    """Print FPS on console
    """
    global fps_time
    os.system('clear')
    try:
        print('FPS: %.0f' % (1 / (time() - fps_time)))
    except:
        None
    fps_time = time()

# Print game state
def print_game_state():
    """Print game state on console
    """
    print("Game State:", game_state.name)

# Print accuracy of image
def print_accuracy_image():
    """Print accuracy of image
    """
    print("Accuracy: %.2f%%" % (accuracy*100))


# Script Start

while True:
    monitor_img = get_monitor_scr()

    # Verify game state
    if game_state == GAME_STATES.GAME_AUTO_OFF:
        find_and_click_img(auto_btn_img, AUTO_THRESHOLD)
    elif game_state == GAME_STATES.GAME_END_MESSAGE:
        find_and_click_img(ok_btn_img, OK_THRESHOLD)
    elif game_state == GAME_STATES.GAME_END_BONUS:
        find_and_click_img(continue_btn_img, CONTINUE_THRESHOLD)
    elif game_state == GAME_STATES.GAME_QUEST_CLEAR:
        find_and_click_img(retry_btn_img, RETRY_THRESHOLD)

    open_image('Image to Match', monitor_img)

    if keyboard.is_pressed('c'):
        break

    print_fps()
    print_game_state()
    print_accuracy_image()
