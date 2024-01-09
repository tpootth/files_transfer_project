def list_files(directory, file_type=None, limit=None):
    import os
    files_list = []
    count = 0

    if limit is not None and limit != '':
        limit = int(limit)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if limit is not None and count >= limit:
                break

            file_path = os.path.join(root, file)
            file_path = file_path.replace('\\', '/')
            file_size_gb = os.path.getsize(file_path) / (1024 * 1024 * 1024)
            file_extension = os.path.splitext(file)[1][1:].lower()

            if file_type is None or file_type.lower() == file_extension:
                files_list.append({
                    "number": count + 1,
                    "file_name": file,
                    "file_path": file_path,
                    "type": file_extension,
                    "size_gb": file_size_gb,
                    "transfer_status": "none"
                })
                count += 1

        if limit is not None and count >= limit:
            break

    return files_list



# ffmpeg -i F:\files_transfer_project\input_test_convert.ts -c:v h264_nvenc F:\files_transfer_project\output_test_convert.mp4