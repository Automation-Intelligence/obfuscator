import pandas as pd
import hashlib
import shutil
import zipfile
import argparse
from pathlib import Path
import sys


def hash_sha256(text):
    """Creates a cryptographic hash of a string to obfuscate confidential information"""
    hash_object = hashlib.sha256(str(text).encode())
    return hash_object.hexdigest()


def obfuscate_1z(_file, column_name, validation=True, delete_original = False):
    """
    Hashes a column in a csv file and removes the original column
    """
    original_filename = _file.stem
    extension = _file.suffix
    directory = _file.parent
    obfuscated_filename = original_filename + '_obfuscated' + extension
    obfuscated_file = directory / obfuscated_filename

    # 1. Read in the file as a pandas dataframe
    df = pd.read_csv(_file, low_memory=False, dtype=str)

    # 2. Create an obfuscated column using the SHA 256 hash of the original column
    obfuscated_col = df[column_name].apply(hash_sha256)

    # 3. Get the index of the original tracking number column and delete the original
    i = df.columns.tolist().index(column_name)
    df.drop(column_name, axis=1, inplace=True)

    # 4. Insert the new column where the original column was
    df.insert(i, f"Obfuscated{column_name}", obfuscated_col)

    # 5. Create a new "obfuscated" file
    df.to_csv(obfuscated_file, index=False)
    del df  # remove the original df from memory

    # 6. If specified, check whether the original and obfuscated files are the same except for the first column
    if validation:
        files_are_equal = True

        # Open the original and transformed files for reading
        with _file.open("r") as original, obfuscated_file.open("r") as transformed:
            # Loop through each line of the original and transformed files
            for orig_line, trans_line in zip(original, transformed):
                orig_fields = orig_line.strip().split(',')
                trans_fields = trans_line.strip().split(',')

                # Compare all fields except the first one
                if orig_fields[1:] != trans_fields[1:]:
                    files_are_equal = False
                    break

        # If the files are the same except for the first column, delete the original file
        if files_are_equal:
            print(f"The {file} files are the same except for the first column. Deleting the original file.")
        else:
            raise ValueError(f"The {file} files are different. Keeping the original file.")

    # 7. if specified, delete the original file
    if delete_original:
        _file.unlink()


def unzip_all_in_directory(_path):
    # Loop through all the zipped files in the directory
    # zipped_files = [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".zip")]
    for _file in _path.glob('*.zip'):
        with zipfile.ZipFile(_file, 'r') as zip_ref:
            for member in zip_ref.namelist():
                if '__MACOSX' not in member:
                    zip_ref.extract(member, _path)
                    # os.remove(_file)  # Optionally, remove the original ZIP file after extraction


def add_csv_extension(_path):
    """ Note that this code assumes all files without an extension in the directory are csv
    """
    for _file in [f for f in list(_path.iterdir()) if '.' not in f.name]:
        if '.' not in _file.name:
            old_file_path = _path / _file.name
            new_file_path = _path / f"{_file.name}.csv"
            shutil.move(old_file_path, new_file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        "Loops through all csv files in a directory and obfuscates a column",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('path', type=Path,
                        help="directory containing the files to be obfuscated\n" 
                             " - Must be absolute path (i.e. /Users/Johndoe/Documents vs ~/Documents)\n"
                             ' - Paths containing spaces must be enclosed in quotes, e.g. "Path to file/"')
    parser.add_argument('column', help='name of the column to obfuscate\n' 
                                       ' - Column names containing spaces must be wrapped in quotes')
    parser.add_argument('-f', "--filenames", nargs='*', type=str,
                        help="specific csv filenames in the directory to obfuscate\n"
                             " - Defaults to all csv files in the directory)\n"
                             ' - Filenames containing spaces must be enclosed in double quotes, e.g. "File 1.csv"')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='deletes the original, unobfuscated files\n(default=False)')
    parser.add_argument('-u', '--unzip', action='store_true',
                        help='unzips all ".zip" files in the directory before obfuscating\n(default=False)')
    parser.add_argument('-c', '--add-csv-extension', action='store_true',
                        help='add ".csv" extension to all files missing an extension in the directory\n(default=False)')
    parser.add_argument('-v', '--validation', action='store_true',
                        help='validates that all columns except for the original / obfuscated columns match\n"'
                             '(default=False)')

    args = parser.parse_args()
    path = args.path
    filenames = args.filenames

    # check if the directory is valid
    if not path.is_dir():
        raise NotADirectoryError(f"The path {path} does not exist or is not a directory")

    # if specific files are specified, only allow csv. Do not allow the -u or -c options.
    if filenames and (args.add_csv_extension or args.unzip):
        parser.error("The -f argument cannot be used with either -u or -c.")

    # instantiate a list of files to obfuscate
    files = []

    # if we're provided individual files, check that they exist and add them to the list
    if filenames:
        for filename in filenames:
            full_path = path / filename
            if not full_path.exists():
                raise FileNotFoundError(f"The file {filename} does not exist in the directory {path}.")
            elif full_path.suffix.lower() != '.csv':
                raise ValueError(f"Invalid file type for {filename}. Expected a .csv file.")
            else:
                files.append(full_path)

    # if no specific files provided, operate on the whole directory
    else:
        # unzip any files if necessary
        if args.unzip:
            unzip_all_in_directory(path)
        # add csv extensions if necessary
        if args.add_csv_extension:
            add_csv_extension(path)
        # add all csv files to list
        files = list(path.glob('*.csv'))

    # check whether there are any csv files to operate on
    if not files:
        print("No csv files in the directory.")
        sys.exit(0)
    else:
        for file in files:
            obfuscate_1z(file, args.column, args.validation, args.delete)