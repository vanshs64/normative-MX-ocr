import os
from google.cloud import vision
from google.protobuf.json_format import MessageToDict
from dotenv import load_dotenv
import io

def extract_text_from_local_pdf(local_pdf_path, output_directory):
    """Extracts text from a local PDF file using Google Cloud Vision API and saves output locally.

    Args:
        local_pdf_path: Path to the local PDF file.
        output_directory: Path to the local directory to save output JSON files.
    """

    load_dotenv()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_CREDENTIAL")

    client = vision.ImageAnnotatorClient()

    with io.open(local_pdf_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    feature = vision.types.Feature(type=vision.enums.Feature.Type.DOCUMENT_TEXT_DETECTION)

    request = vision.types.AnnotateImageRequest(image=image, features=[feature])

    response = client.annotate_image(request=request)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(response.error.message))

    # Convert the protobuf response to a Python dictionary
    response_dict = MessageToDict(response)

    # Save the JSON output to a local file
    output_filename = os.path.splitext(os.path.basename(local_pdf_path))[0] + ".json"
    output_path = os.path.join(output_directory, output_filename)

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    import json
    with open(output_path, 'w') as outfile:
        json.dump(response_dict, outfile, indent=4)

    print(f"Output saved to {output_path}")


if __name__ == "__main__":
    local_pdf_path = "testT4.pdf"
    output_directory = "goofyOutput"  # Directory where JSON output will be saved

    extract_text_from_local_pdf(local_pdf_path, output_directory)

