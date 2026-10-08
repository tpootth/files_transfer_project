import json
import os


def load_json(path):
    """Return the list stored in ``path`` or an empty list if the file does not exist."""
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(data, path):
    """Write ``data`` atomically so a crash never leaves a half-written file."""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    tmp_path = path + '.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    os.replace(tmp_path, path)


def save_to_json(data, output_file):
    """Merge ``data`` into ``output_file``.

    Files already present (same ``file_path``) are kept as they are so their
    ``transfer_status`` is not reset; only new files are appended. Entries are
    renumbered afterwards. Returns the number of new entries added.
    """
    existing_data = load_json(output_file)
    known_paths = {item['file_path'] for item in existing_data}

    new_items = [item for item in data if item['file_path'] not in known_paths]
    merged = existing_data + new_items
    for number, item in enumerate(merged, start=1):
        item['number'] = number

    write_json(merged, output_file)
    return len(new_items)
