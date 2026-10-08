"""Scan a directory and record the files found in a JSON file.

Example:
    python main.py G:/ -o F:/files_transfer_project/file_details.json -t ts -l 5
"""
import argparse

from module.list_files import list_files
from module.save_to_json import save_to_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('directory_path', help='directory to scan (recursive)')
    parser.add_argument('-o', '--output-json', default='file_details.json',
                        help='JSON file to write (default: %(default)s)')
    parser.add_argument('-t', '--file-type', default=None,
                        help='only keep files with this extension, e.g. ts')
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help='maximum number of files to record')
    args = parser.parse_args(argv)

    file_details = list_files(args.directory_path, args.file_type, args.limit)
    added = save_to_json(file_details, args.output_json)
    print(f"Found {len(file_details)} file(s), {added} new, saved to {args.output_json}")


if __name__ == '__main__':
    main()
