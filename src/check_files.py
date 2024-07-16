import pandas as pd
import os
import sys

# Define the expected columns and their data types
expected_columns = {
    'column1': 'int64',
    'column2': 'float64',
    'column3': 'object',
    'column4': 'datetime64[ns]',
    'column5': 'bool'
}

checked_files_path = 'checked_files.txt'

def load_checked_files():
    if os.path.exists(checked_files_path):
        with open(checked_files_path, 'r') as file:
            return set(file.read().splitlines())
    return set()

def save_checked_file(file_path):
    with open(checked_files_path, 'a') as file:
        file.write(file_path + '\n')

def validate_file(file_path):
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            print(f"Unsupported file format: {file_path}")
            return False

        for column, dtype in expected_columns.items():
            if column not in df.columns:
                print(f"Missing column: {column} in {file_path}")
                return False
            if df[column].dtype != dtype:
                print(f"Incorrect dtype for column {column} in {file_path}. Expected {dtype}, got {df[column].dtype}")
                return False

        print(f"{file_path} is valid.")
        return True

    except Exception as e:
        print(f"Error validating file {file_path}: {e}")
        return False

def validate_all_files(directory):
    checked_files = load_checked_files()
    valid = True
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.csv', '.xls', '.xlsx')):
                file_path = os.path.join(root, file)
                if file_path not in checked_files:
                    if validate_file(file_path):
                        save_checked_file(file_path)
                    else:
                        valid = False
    return valid

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_files.py <directory>")
        exit(1)
    directory = sys.argv[1]
    if validate_all_files(directory):
        print("All files are valid.")
        exit(0)
    else:
        print("Some files are invalid.")
        exit(1)
