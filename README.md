# Confidential Information Obfuscator
Operates on csv files. Specify a directory or specific files and the name of the column containing the confidential information that needs to be obfuscated. This script will replace that column with a SHA 256 hash of the orignal values. See the usage below for additional options when running the script. 

```
% python obfuscator.py -h
usage: Loops through all csv files in a directory and obfuscates a column
       [-h] [-f FILENAMES [FILENAMES ...]] [-d] [-u] [-c] [-v] path column

positional arguments:
  path                  directory containing the files to be obfuscated
                         - Must be absolute path (i.e. /Users/Johndoe/Documents vs ~/Documents)
                         - Paths containing spaces must be enclosed in quotes, e.g. "Path to file/"
  column                name of the column to obfuscate
                         - Column names containing spaces must be wrapped in quotes

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAMES [FILENAMES ...], --filenames FILENAMES [FILENAMES ...]
                        specific csv filenames in the directory to obfuscate
                         - Defaults to all csv files in the directory)
                         - Filenames containing spaces must be enclosed in double quotes, e.g. "File 1.csv"
  -d, --delete          deletes the original, unobfuscated files
                        (default=False)
  -u, --unzip           unzips all ".zip" files in the directory before obfuscating
                        (default=False)
  -c, --add-csv-extension
                        add ".csv" extension to all files missing an extension in the directory
                        (default=False)
  -v, --validation      validates that all columns except for the original / obfuscated columns match
                        "(default=False)
```
