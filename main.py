import mss
import cv2
import numpy as np

sct = mss.mss()

# Constants
# Threshold
bluestacks_threshold = .90
# Box Drawing
box_color = (0, 255, 0)
box_border_width = 2

# Target Imgs
bluestacks_logo_img = cv2.imread('assets/bluestacks.png')
bluestacks_size_img = cv2.imread('assets/bluestacks_size.png')

# Get monitor screen
monitor_scr = sct.shot()
monitor_img = cv2.imread(monitor_scr)

# Match bluestacks windows
match_bluestacks = cv2.matchTemplate( monitor_img, bluestacks_logo_img, cv2.TM_CCOEFF_NORMED)

bluestacks_min_val, bluestacks_max_val, bluestacks_min_loc, bluestacks_max_loc = cv2.minMaxLoc(
    match_bluestacks)

print('Accuracy of bluestacks window: %.2f%%' % bluestacks_max_val)

bluestacks_w = bluestacks_size_img.shape[1]
bluestacks_h = bluestacks_size_img.shape[0]

# Check if max match value is above threshold
if bluestacks_max_val > bluestacks_threshold:
    # Get dimesion of bluestacks window
    dimensions_bluestacks = {
        'left': bluestacks_max_loc[0],
        'top': bluestacks_max_loc[1],
        'width': bluestacks_w,
        'height': bluestacks_h
    }

    bluestacks_scr = np.array(sct.grab(dimensions_bluestacks))
    # Cut off alpha
    bluestacks_window = bluestacks_scr[:,:,:3]


    cv2.imshow('Bluestacks window', bluestacks_scr)
    cv2.waitKey()
    cv2.destroyAllWindows()
else:
    print('Bluestacks window not found. Check if the program is open, not minimized and in your primary monitor')
