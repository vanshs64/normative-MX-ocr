# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# [START documentai_process_document]
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud import documentai  # type: ignore

from google.auth import default as google_auth_default
from google.oauth2 import service_account

from helpers import save_text_to_file
import os
from dotenv import load_dotenv


load_dotenv()  # This loads variables from .env into os.environ

service_account_key = os.getenv("SERVICE_ACCOUNT_KEY")
if not service_account_key:
    raise ValueError("SERVICE_ACCOUNT_KEY not found in environment. Check your .env file.")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key

project_id = "509669788392"
location = "us" # Format is "us" or "eu"
processor_id = "4da2c852ac4058eb" # Create processor before running sample
file_path = "T4Vansh.pdf"
mime_type = "application/pdf" # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
field_mask = "text,entities,pages.pageNumber"  # Optional. The fields to return in the Document object.
# processor_version_id = "YOUR_PROCESSOR_VERSION_ID" # Optional. Processor version to use

def process_document_sample(
    project_id=project_id,
    location=location,
    processor_id=processor_id,
    file_path=file_path,
    mime_type=mime_type,
    processor_version_id: Optional[str] = None,
) -> None:
    # You must set the `api_endpoint` if you use a location other than "us".
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    # THE KEY line of code I needed
    credentials = service_account.Credentials.from_service_account_file(GOOGLE_APPLICATION_CREDENTIALS)

    client = documentai.DocumentProcessorServiceClient(client_options=opts, credentials=credentials)

    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        # The full resource name of the processor, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}`
        name = client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    print(f"Read {len(image_content)} bytes from file {file_path}")


    # Load binary data
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # For more information: https://cloud.google.com/document-ai/docs/reference/rest/v1/ProcessOptions
    # Optional: Additional configurations for processing.
    process_options = documentai.ProcessOptions(
        # Process only specific pages
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
            pages=[1]
        )
    )

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )

    print("Sending request to Document AI...")


    result = client.process_document(request=request)

    print("Received response from Document AI")


    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    document = result.document

    # Read the text recognition output from the processor
    print("The document contains the following text:")
    print(document.text)

    save_text_to_file(document.text, "google_testing.txt")
    print("Text saved to google_testing.txt")


process_document_sample()

# [END documentai_process_document]