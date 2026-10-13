"""Convert the videos listed in a JSON file (created by main.py) to MP4.

Progress is written back to the JSON file after every video, so the script can be
stopped and run again: videos with transfer_status "success" are skipped.

Example:
    python convert_video.py -j F:/files_transfer_project/file_details.json \
        -o F:/files_transfer_project/output_video -f ts -l 20
"""
import argparse
import os
from collections import Counter

from module.convert_to_mp4 import DEFAULT_VIDEO_CODEC, convert_to_mp4
from module.save_to_json import load_json, write_json

# Extensions converted when no --file-filter is given. mp4 is left out because it is the target format.
VIDEO_EXTENSIONS = {'ts', 'm2ts', 'mts', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mpg', 'mpeg',
                    'm4v', '3gp', 'vob'}


def output_name(item, output_path, duplicate_name):
    """Build the MP4 path. Files sharing a name with another file get their number appended."""
    base = os.path.splitext(item['file_name'])[0]
    if duplicate_name:
        base = f"{base}_{item['number']}"
    return os.path.join(output_path, base + '.mp4')


def process_videos(json_file_path, output_path, limit_video=None, file_filter=None,
                   video_codec=DEFAULT_VIDEO_CODEC, retry_failed=False):
    data = load_json(json_file_path)

    if file_filter:
        file_filter = file_filter.lower().lstrip('.')
        candidates = [item for item in data if item['type'].lower() == file_filter]
    else:
        candidates = [item for item in data if item['type'].lower() in VIDEO_EXTENSIONS]

    todo_status = {'none', 'failed'} if retry_failed else {'none'}
    todo = [item for item in candidates if item['transfer_status'] in todo_status]
    if limit_video:
        todo = todo[:limit_video]

    # Count base names over all candidates so the chosen output name stays stable between runs.
    base_names = Counter(os.path.splitext(item['file_name'])[0].lower() for item in candidates)

    print(f"{len(todo)} video(s) to convert")
    success = failed = 0
    for index, item in enumerate(todo, start=1):
        duplicate_name = base_names[os.path.splitext(item['file_name'])[0].lower()] > 1
        output_file = output_name(item, output_path, duplicate_name)

        print(f"[{index}/{len(todo)}] input : {item['file_path']}")
        print(f"[{index}/{len(todo)}] output: {output_file}")

        if os.path.exists(output_file):
            print("Output already exists, marking as success")
            ok = True
        elif not os.path.exists(item['file_path']):
            print("Input file not found")
            ok = False
        else:
            ok = convert_to_mp4(item['file_path'], output_file, video_codec)

        item['transfer_status'] = 'success' if ok else 'failed'
        item['output_path'] = output_file.replace('\\', '/') if ok else None
        success += ok
        failed += not ok
        write_json(data, json_file_path)

    print(f"Done: {success} success, {failed} failed")
    return success, failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('-j', '--json-file', default='file_details.json',
                        help='JSON file created by main.py (default: %(default)s)')
    parser.add_argument('-o', '--output-path', default='output_video',
                        help='folder for the MP4 files (default: %(default)s)')
    parser.add_argument('-l', '--limit', type=int, default=None,
                        help='maximum number of videos to convert in this run')
    parser.add_argument('-f', '--file-filter', default=None,
                        help='only convert this extension, e.g. ts (default: common video types except mp4)')
    parser.add_argument('-c', '--codec', default=DEFAULT_VIDEO_CODEC,
                        help='ffmpeg video codec: h264_nvenc (GPU) or libx264 (CPU) (default: %(default)s)')
    parser.add_argument('--retry-failed', action='store_true',
                        help='also retry videos whose previous conversion failed')
    args = parser.parse_args(argv)

    process_videos(args.json_file, args.output_path, args.limit, args.file_filter,
                   args.codec, args.retry_failed)


if __name__ == '__main__':
    main()
