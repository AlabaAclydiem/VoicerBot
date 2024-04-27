import os


def delete_files(file_paths):
    for file_path in file_paths:
        if file_path is not None and os.path.exists(file_path):
            os.remove(file_path)