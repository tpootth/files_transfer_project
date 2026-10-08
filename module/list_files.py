import os


def list_files(directory, file_type=None, limit=None):
    """Walk ``directory`` and return details of the files found.

    file_type: extension to keep (e.g. ``'ts'`` or ``'.ts'``), case-insensitive.
               ``None`` or ``''`` keeps every file.
    limit:     maximum number of files to return. ``None``, ``''`` or ``0`` means no limit.
    """
    file_type = (file_type or '').lower().lstrip('.') or None
    limit = int(limit) if limit not in (None, '') else None
    if limit is not None and limit <= 0:
        limit = None

    files_list = []
    for root, dirs, files in os.walk(directory):
        dirs.sort()
        for file in sorted(files):
            if limit is not None and len(files_list) >= limit:
                return files_list

            file_extension = os.path.splitext(file)[1][1:].lower()
            if file_type is not None and file_type != file_extension:
                continue

            file_path = os.path.join(root, file).replace('\\', '/')
            try:
                file_size = os.path.getsize(file_path)
            except OSError as e:
                print(f"Skip {file_path}: {e}")
                continue

            files_list.append({
                "number": len(files_list) + 1,
                "file_name": file,
                "file_path": file_path,
                "type": file_extension,
                "size_gb": round(file_size / (1024 ** 3), 4),
                "transfer_status": "none",
            })

    return files_list
