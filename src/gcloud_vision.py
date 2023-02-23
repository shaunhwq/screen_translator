import cv2
import json
import base64
import requests
import numpy as np
from typing import Tuple, List


class Paragraph:
    def __init__(self):
        self.boundary: np.array = None
        self.num_lines: int = 0
        self.text: str = ""
        self.languages: set = set()  # Currently not in use


def ocr(image: np.array, api_key: str) -> Tuple[bool, dict]:
    """
    Performs OCR with Google Cloud Vision API Service
    :param image: Image to perform OCR on
    :param api_key: Google Cloud API Key
    :return: let R = return variable. R[0] => success/failed, R[1] => Error msg if failed, Json if
    """
    retval, buffer = cv2.imencode('.jpg', image)
    image_b64 = base64.b64encode(buffer).decode()

    url = f"https://vision.googleapis.com/v1/images:annotate"
    body = {
        "requests": [
            {
                "image": {"content": image_b64},
                "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                "imageContext": {"languageHints": ["zh-Hans", "zh-Hant"]}
            }
        ]
    }
    response = requests.post(
        url=url,
        data=json.dumps(body),
        params={"key": api_key},
    )

    return response.status_code == 200, response.json()


def process_ocr_response(response_dict: dict) -> List[Paragraph]:
    """
    Retrieves all paragraphs from the OCR request.

    :param response_dict: response.json() object from google OCR
    :return: A list of Paragraph objects
    """
    annotation = response_dict["responses"][0]["fullTextAnnotation"]
    paragraphs = []

    for page in annotation["pages"]:
        for block in page["blocks"]:
            for paragraph in block["paragraphs"]:
                para_obj = Paragraph()
                for word in paragraph["words"]:
                    for symbol in word["symbols"]:
                        para_obj.text += symbol["text"]
                        try:
                            break_type = symbol["property"]["detectedBreak"]["type"]
                            if break_type == "SPACE":
                                para_obj.text += " "
                            elif break_type == "EOL_SURE_SPACE":
                                para_obj.text += "  "
                                para_obj.num_lines += 1
                            if break_type == "LINE_BREAK":
                                para_obj.text += " "
                                para_obj.num_lines += 1
                        except KeyError:
                            pass  # No property is ok
                    try:
                        languages = word["property"]["detectedLanguages"]
                        para_obj.languages.update(set([lang.get("languageCode", "unknown") for lang in languages]))
                    except KeyError:
                        pass
                vertices = np.array([[v.get("x", 0), v.get("y", 0)] for v in paragraph["boundingBox"]["vertices"]])
                para_obj.boundary = vertices
                paragraphs.append(para_obj)
    return paragraphs
