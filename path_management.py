from os.path import join as p_join
from os import walk


def make_paths(input_folder):
    walker = walk(input_folder)
    paths = []
    for directory, subdir, files in walker:
        if directory == input_folder:
            for file in files:
                file_path = p_join(directory, file)
                paths.append(file_path)
    return paths