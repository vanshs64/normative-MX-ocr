from cer import levenshtein_distance
from pathlib import Path
import json
import csv
from tqdm import tqdm

doc_types = ["T1", "T4", "FS"]
current_ocr = "GPT"

TEST_PATH = "../test_docs/test_study_data"

def append_score_to_csv():
    return

def main():
    names = []
    with open("../test_docs/names.txt", "r") as list_of_files:
        names = list_of_files.read().split() # put names into an array (iterable)

    # for each person in our study
    for name in names:
        name_CER = [name] # all the CER rates for this person's documents in order, T1, T4, FS

        # for each document that person has
        for doc_type in doc_types:

            doc_ref_data = []
            doc_hyp_data = []

            hyp_file_name = f"{doc_type}{name}{current_ocr}Hyp.txt"
            ref_file_name = f"{doc_type}{name}Ref.txt"

            hyp_file_path = Path(TEST_PATH) / f"{name}Hyp" / hyp_file_name
            ref_file_path = Path(TEST_PATH) / f"{name}Ref" / ref_file_name
            # for this person, this document, what is the error
            total_errors = 0
            total_chars = 0

            comparison_table = []
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

                    doc_ref_data.append(reference_value)
                    doc_hyp_data.append(hypothesis_value)

                    # since N/A is just for display, in actual CER calc we use empty string (0 characters) therefore do this
                    reference_value = '' if reference_value == 'N/A' else ''
                    hypothesis_value = '' if hypothesis_value == 'N/A' else ''

                    # actual calculation
                    distance = levenshtein_distance(hypothesis_value, reference_value)
                    
                    total_errors += distance
                    total_chars += len(reference_value)
                
                print(f"Currect Doc: {doc_type}")

            # Calculate overall CER
            overall_cer = total_errors / total_chars if total_chars > 0 else 0.0
            name_CER.append(overall_cer)
        
        # name_CER has 3 items, each one is a CER number for each doc type
        with open(f"../test_docs/{current_ocr}Results.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(name_CER)
        
            print(f"Done CER calcs and saved data for person: {name}")
    print("Done all CER for each person in names.txt")



if __name__ == "__main__":
    main()