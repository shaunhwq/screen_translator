import cv2
import argparse
from src.Window import get_selected_windows
from src.utils import translate_image


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--names", help="Gets windows with name...", nargs="+", default=["Zoom", "VooV", "WeCom", "Chrome"])
    args = parser.parse_args()

    windows = get_selected_windows(args.names)
    print([(i, win.name) for (i, win) in enumerate(windows)])
    app_window = windows[int(input("Selected Window No: "))]

    cv2_window_title = "Translated"
    translated_overlay = None
    cv2.namedWindow(cv2_window_title, cv2.WINDOW_NORMAL)

    while True:
        frame = app_window.get_screenshot()
        if translated_overlay is not None:
            frame[translated_overlay > 0] = translated_overlay[translated_overlay > 0]
        cv2.imshow(cv2_window_title, frame)

        key = cv2.waitKey(1) & 255
        if key == 27:  # Esc
            break
        elif key == ord("c"):
            translated_overlay = translate_image(frame)

    cv2.destroyAllWindows()