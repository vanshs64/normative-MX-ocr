HYPOTHESIS_PATH = "../test_docs/hypotheses"
REFERENCE_PATH = "../test_docs/reference"

from pathlib import Path
import json

file_name = "T1John.txt"


hyp_file_path = Path(HYPOTHESIS_PATH) / file_name
ref_file_path = Path(REFERENCE_PATH) / file_name

comparison_table = []

with open(hyp_file_path, "r") as hyp_file, open(ref_file_path, "r") as ref_file:
    hyp_content = hyp_file.read()
    hyp_content_dict = json.loads(hyp_content)

    ref_content = ref_file.read()
    ref_content_dict = json.loads(ref_content)

    for key in ref_content_dict.keys():
        comparison_table.append([
            key, 
            hyp_content_dict.get(key, "N/A"), 
            ref_content_dict.get(key, "N/A")
        ])

    print(comparison_table)





















# import os
# import ast

# expectation_key = []
# # Construct the absolute path to the file
# current_dir = os.path.dirname(os.path.abspath(__file__))
# file_path = os.path.abspath(os.path.join(current_dir, "..", "test_docs", "truths", "T1John.txt"))

# with open(file_path, "r") as f:
#     truths_dict = ast.literal_eval(f.read())  # Assuming the file contains a dictionary in string format
#     expectation_key = list(truths_dict.keys())

# print(expectation_key)