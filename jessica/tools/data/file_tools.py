import os


def create_directory(path):

    if not os.path.exists(path):
        os.makedirs(path)
        return f"Directory created: {path}"

    return f"Directory already exists: {path}"


def write_file(path, content):

    with open(path, "w") as f:
        f.write(content)

    return f"File written: {path}"
