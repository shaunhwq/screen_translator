import os
import cv2
import argparse
from src.utils import translate_image


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Image to translate", required=True)
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise FileNotFoundError(f"Unable to find file {args.input}")

    input_image = cv2.imread(args.input)
    translated_image = translate_image(input_image)
    input_image[translated_image > 0] = translated_image[translated_image > 0]

    cv2.imshow("Translated", input_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
