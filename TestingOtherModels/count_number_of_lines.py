import os

def count_lines_in_directory(directory):
    line_count = 0
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    line_count += sum(1 for _ in f)
    return line_count

directory_path = "/Users/lucasvilsen/Desktop/GrammatikTAK/GrammatiktakBackend"
total_lines = count_lines_in_directory(directory_path)
print(f"Total lines in .py files: {total_lines}")