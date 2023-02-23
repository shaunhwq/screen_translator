from typing import List, Tuple, Optional
import cv2
import numpy as np
from googletrans import Translator
import hanzidentifier
import os
import src.gcloud_vision as gcloud_vision


def split_str_into_n_lines(string: str, n_lines: int) -> List[str]:
    """
    Somewhat hacky solution for this problem but it works.

    Splits a paragraph into multiple lines, around the same length for each

    :param string: Literally a paragraph
    :param n_lines: Number of lines we want to display the paragraph in
    :return: Returns a list of strings which were split from the paragraph
    """
    if n_lines == 1:
        return [string]

    total_length = len(string)
    desired_line_length = total_length // n_lines
    para_lines = []
    sum_chars = 0
    line_words = []
    for word in string.split():
        if sum_chars < desired_line_length:
            # Add to line
            line_words.append(word)
            sum_chars += len(word) + 1
        else:
            # Create new line
            para_lines.append(" ".join(line_words))
            line_words = [word]
            sum_chars = len(word) + 1
    if len(line_words) != 0:
        para_lines.append(" ".join(line_words))
    return para_lines


def get_cv2_font_size(string: str, max_width: float, cv2_font: int = cv2.FONT_HERSHEY_COMPLEX_SMALL) -> float:
    """
    Estimates the best text font size using binary search. in a particular font given the width constraint.

    :param string: String you want to place with cv2.putText
    :param max_width: Maximum width of string
    :param cv2_font: cv2 font to use
    :return: cv2.putText font_size you should use to fit into max_width
    """
    min_font_size, max_font_size = 0.01, 4
    max_iter, counter = 20, 0

    while True:
        font_size = (max_font_size + min_font_size) / 2
        (text_width, text_height), baseline = cv2.getTextSize(string, cv2_font, font_size, 1)

        if max_width * 0.975 < text_width < max_width:
            return font_size
        elif text_width < max_width:
            min_font_size = font_size + 0.01
        else:
            max_font_size = font_size - 0.01
        counter += 1
        if counter == max_iter:
            print("unable to estimate best font size")
            break

    return 0.3


def get_n_most_freq_color(image: np.array, n: int) -> List:
    """
    Returns N most frequent colors
    :param image: Image to check
    :param n: Number of colors to return
    :return: A list of colors, from least frequent to most frequent
    """
    pixels = np.float32(image.reshape(-1, 3))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    _, labels, palette = cv2.kmeans(pixels, n, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    _, counts = np.unique(labels, return_counts=True)
    palette = palette.astype(np.uint8)
    palette = [x.tolist() for _, x in sorted(zip(counts, palette))]
    return palette[:n]


def translate_image(image: np.array) -> np.array:
    """
    Detect text
    :param image:
    :param feature_type:
    :return:
    """
    overlay = np.zeros_like(image)

    api_key = os.environ["GCLOUD_API_KEY"]
    assert api_key is not None, "Env var GCLOUD_API_KEY is not set"

    ret, response = gcloud_vision.ocr(image, api_key)
    if not ret:
        # should use logger
        print(f"Unable to get response [200]. Err: {response}")
        return None

    paragraphs = gcloud_vision.process_ocr_response(response)

    paragraphs = [p for p in paragraphs if hanzidentifier.has_chinese(p.text)]
    translator = Translator()
    translations = translator.translate([p.text for p in paragraphs], dest="en")

    for paragraph, translated in zip(paragraphs, translations):
        vertices = paragraph.boundary
        if cv2.contourArea(vertices) < 250:
            continue
        # https://stackoverflow.com/questions/15956124/minarearect-angles-unsure-about-the-angle-returned
        # TODO: HANDLE ROTATED TEXT
        #    https://theailearner.com/2020/11/02/how-to-write-rotated-text-using-opencv-python/
        # TODO: Draw out the min area rect to see if its suitable
        (center_x, center_y), (height, width), angle = cv2.minAreaRect(vertices)

        img_crop = image[int(vertices[1][1]): int(vertices[2][1]), int(vertices[0][0]): int(vertices[1][0])]
        try:
            font_color, bg_color = get_n_most_freq_color(img_crop, 2)
            overlay[int(vertices[1][1]): int(vertices[2][1]), int(vertices[0][0]): int(vertices[1][0])] = bg_color
        except cv2.error:
            overlay[int(vertices[1][1]): int(vertices[2][1]), int(vertices[0][0]): int(vertices[1][0])] = [1, 1, 1]
            font_color = (255, 255, 255)

        lines = split_str_into_n_lines(translated.text, paragraph.num_lines)
        lines_length = [len(line) for line in lines]

        font = cv2.FONT_ITALIC
        max_height, max_width = min(width, height) / len(lines), max(width, height)
        max_length_line = lines[lines_length.index(max(lines_length))]
        # TODO: Set max size = 1
        font_size = min(1, get_cv2_font_size(max_length_line, max_width, font))
        (final_width, final_height), _ = cv2.getTextSize(max_length_line, font, font_size, 1)
        buffer = (max_height * len(lines) - final_height * len(lines)) // (2 + len(lines) - 1)
        for i, line in enumerate(lines):
            text_position = (int(vertices[0][0]), int(vertices[0][1] + (i + 1) * (final_height + buffer)))
            cv2.putText(overlay, line, text_position, font, font_size, font_color, 1)

    return overlay
