from cer import levenshtein_distance
from pathlib import Path
import json
import csv
# Removed unused tqdm import

doc_types = ["T1", "T4", "FS"]


TEST_PATH = "../test_docs/test_study_data"
NAMES_PATH = "../test_docs/names.txt"


def append_score_to_csv(name, ocr_name):
        print(f"Generating CER Scores for {name}")
        name_CER = [name] # all the CER rates for this person's documents in order, T1, T4, FS

        # for each document that person has
        for doc_type in doc_types:
            print(f"Currect Doc: {doc_type}")

            hyp_file_name = f"{doc_type}{name}{ocr_name}Hyp.txt"
            ref_file_name = f"{doc_type}{name}Ref.txt"

            hyp_file_path = Path(TEST_PATH) / f"{name}Hyp" / hyp_file_name
            ref_file_path = Path(TEST_PATH) / f"{name}Ref" / ref_file_name
            # for this person, this document, what is the error
            total_errors = 0
            total_chars = 0

            # Removed unused comparison_table variable
            with open(hyp_file_path, "r") as hyp_file, open(ref_file_path, "r") as ref_file:
                hyp_content = hyp_file.read()
                ref_content = ref_file.read()

                hyp_content_dict = json.loads(hyp_content)
                ref_content_dict = json.loads(ref_content)

                # for each extracted value, determine error
                # each key is one of the rows of the extracted data from this document "doc_type"
                for key in ref_content_dict.keys():
                    # if the key doesn't exist, make it empty '' (so that there are no possibilities for Null or Undefined)
                    # + formatting, str, strip
                    reference_value = str(ref_content_dict.get(key, "'N/A'")).strip()
                    hypothesis_value = str(hyp_content_dict.get(key, "N/A")).strip()

                    # since N/A is just for display, in actual CER calc we use empty string (0 characters) therefore do this
                    reference_value = '' if reference_value == 'N/A' else reference_value
                    hypothesis_value = '' if hypothesis_value == 'N/A' else hypothesis_value

                    # actual calculation
                    distance = levenshtein_distance(hypothesis_value, reference_value)
                    
                    total_errors += distance
                    total_chars += len(reference_value)
                

            # Calculate overall CER
            overall_cer = total_errors / total_chars if total_chars > 0 else 0.0
            name_CER.append(overall_cer)
        
        # name_CER has 3 items, each one is a CER number for each doc type
        with open(f"../test_docs/{ocr_name}Results.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(name_CER)
        
            print(f"Done CER calcs and saved data for person: {name}")


if __name__ == "__main__":
    append_score_to_csv()