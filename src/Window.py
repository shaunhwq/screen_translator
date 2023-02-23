import numpy as np
import sys
import pyautogui
import cv2
import platform
if platform.system() == "Windows":
    import pygetwindow._pygetwindow_win as gw
elif platform.system() == "Darwin":  # MacOS
    import pygetwindow._pygetwindow_macos as gw
else:
    raise NotImplementedError(f"System not supported: {platform.system()}")


class Window:
    def __init__(self, name):
        self.name = name
        self.position = None
        self.get_position()

    def get_position(self):
        position = list(map(lambda x: int(x), gw.getWindowGeometry(self.name)))
        if position is None and self.position is None:
            sys.exit(f"Unable to find the position of {self.name}")

        if position is None:
            # last known position
            return self.position

        return position

    def get_screenshot(self):
        y, x, h, w = self.get_position()
        # PIL Image, need to convert
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Grab window location
        screenshot = screenshot[x: x + w, y: y + h, :]
        return screenshot


def get_selected_windows(names_filter):
    windows = []
    for window_name in gw.getAllTitles():
        # windows.append(Window(window_name))
        for app_name in names_filter:
            if app_name in window_name:
                windows.append(Window(window_name))
    return windows
