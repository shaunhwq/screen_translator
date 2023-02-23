# Screen Translator
- Image translation from Chinese to English.
- Mainly for aiding understanding during presentations, when slides are in Chinese.

### Alternative solutions:

| Solution                          | Benefits                                 | Drawbacks                                                                                    |
|-----------------------------------|------------------------------------------|----------------------------------------------------------------------------------------------|
| Google Lens/Translate with Camera | - Real-time translation for presentation | - Manually hold phone <br> - Small display <br> - Introduce distortion in images (e.g. blur) |

### Solution
1. Receive video feed from meeting app
2. When translate button is pressed, image is sent for translation
3. Translated text is overlaid onto original image for display. Will attempt to preserve word and background color.


## Installation

```shell
virtualenv venv
source venv/bin/activate
# Screen translated_overlay related
pip3 install pyautogui pygetwindow
# Image related manipulation and text overlay
pip3 install opencv-python
# For OCR
pip3 install google-cloud-vision
# https://stackoverflow.com/questions/52455774/googletrans-stopped-working-with-error-nonetype-object-has-no-attribute-group
# Free google translate
pip3 install googletrans==3.1.0.a0
```


## Usage

Note: Ensure that this app has the relevant permissions (screenshot). Your PC should prompt you when you start the program.

First, add your API key and activate your virtual environment:

- [How to get your API key](https://support.google.com/googleapi/answer/6158862?hl=en)
```commandline
export GCLOUD_API_KEY=YOUR_API_KEY
source venv/bin/activate
```

Running screen translator:

- After you have started, select the desired window in your terminal.
- Press C to translate.
```commandline
python3 main.py
```

For testing purposes:
```commandline
python3 test.py -i assets/test_image.png
```


## Limitations:
1. Desired window must be in the foreground.
2. Button has to be pressed [<b><u>c</u></b>] to translate the image.
3. If window name keeps changing, we are unable to update the position of the window. Make sure that the window you wish
   to translate is positioned properly first.
4. Chinese meetings only for now.

## Future work:
1. Speech to text translation (e.g. subtitles)
2. Extend detected text regions if there not much features detected.
3. Scene change detection to automatically send for translation
4. Could use underlying libraries (Quartz) and remove dependencies for pyautogui and pygetwindow