def file_content(path: str):
    with open(path, "r") as file:
        content = file.read()
    return content