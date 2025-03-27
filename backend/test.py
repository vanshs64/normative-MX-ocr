import os
import ast

expectation_key = []
# Construct the absolute path to the file
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.abspath(os.path.join(current_dir, "..", "test_docs", "truths", "T1John.txt"))

with open(file_path, "r") as f:
    truths_dict = ast.literal_eval(f.read())  # Assuming the file contains a dictionary in string format
    expectation_key = list(truths_dict.keys())

print(expectation_key)