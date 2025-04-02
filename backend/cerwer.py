import fastwer
import os
import ast

def evaluate_ocr(reference_text, hypothesis_text):
    cer = fastwer.score_sent(reference_text, hypothesis_text, char_level=True)
    wer = fastwer.score_sent(reference_text, hypothesis_text)
    return cer, wer

current_dir = os.path.dirname(os.path.abspath(__file__))
reference_path = os.path.abspath(os.path.join(current_dir, "..", "test_docs", "truths", "T1John.txt"))
hypothesis_path = "extracted_text.txt"


with open(reference_path, "r") as f:
    truths_dict = ast.literal_eval(f.read())  # Assuming the file contains a dictionary in string format
    expectation_key = list(truths_dict.keys())

reference = ""

