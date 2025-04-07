import os
import shutil

def reorganize_files(main_directory):
    # Iterate through the folders in the main directory
    for folder in os.listdir(main_directory):
        folder_path = os.path.join(main_directory, folder)
        
        # Skip if it's not a directory
        if not os.path.isdir(folder_path):
            continue
        
        # Iterate through the files in the folder
        for file_name in os.listdir(folder_path):
            # Process files with .pdf or .txt extensions
            if file_name.endswith(".pdf") or file_name.endswith(".txt"):
                parts = file_name.split(".")[0]  # Remove the file extension
                person_name = parts[2:]  # Extract the name (e.g., "Bob" from "T1Bob" or "T1BobRef")
                
                # Create a directory for the person if it doesn't exist
                person_dir = os.path.join(main_directory, person_name)
                os.makedirs(person_dir, exist_ok=True)
                
                # Move the file to the person's directory
                source_file = os.path.join(folder_path, file_name)
                destination_file = os.path.join(person_dir, file_name)
                shutil.move(source_file, destination_file)

# Specify the main directory containing the T1, T4, and FS folders
main_directory = "test_study_data"
reorganize_files(main_directory)