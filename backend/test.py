HYPOTHESIS_PATH = "../test_docs/test_study_docs/EmilyHyp"
REFERENCE_PATH = "../test_docs/test_study_docs/EmilyRef"

from pathlib import Path
import json

hyp_file_path = HYPOTHESIS_PATH + "/T1EmilyGPTHyp.txt"
ref_file_path = REFERENCE_PATH + "/T1EmilyRef.txt"

print(hyp_file_path)
print(ref_file_path)

comparison_table = []


doc_type="T1"
name="Emily"

template_file_name = f"{doc_type}{name}Ref.txt"
key_template_path = f"../test_docs/test_study_data/{name}Ref/{template_file_name}"
key_template = ""
with open(key_template_path, "r") as f:
    key_template = f.read()
    key_template_dict = json.loads(key_template)
    key_template = list(key_template_dict.keys())

print(key_template)

# with open("../test_docs/test_study_data/EmilyHyp/T1EmilyGPTHyp.txt", "r") as hyp_file, open(ref_file_path, "r") as ref_file:
#     hyp_content = hyp_file.read()
#     hyp_content_dict = json.loads(hyp_content)

#     ref_content = ref_file.read()
#     ref_content_dict = json.loads(ref_content)

#     for key in ref_content_dict.keys():
#         comparison_table.append([
#             key, 
#             hyp_content_dict.get(key, "N/A"), 
#             ref_content_dict.get(key, "N/A")
#         ])

#     print(comparison_table)





















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