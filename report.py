import os

def count_files_in_directory(directory_path):
    """Counts the number of files in a directory, excluding subdirectories.
    
    Args:
        directory_path: The path to the directory.
    
    Returns:
        The number of files in the directory, or None if the directory does not exist.
    """
    if not os.path.isdir(directory_path):
        return None
    
    file_count = 0
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            file_count += 1
    
    return file_count


print(count_files_in_directory('./webpages'))