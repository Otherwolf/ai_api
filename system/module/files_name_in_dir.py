import os, fnmatch


# Взять наименование файлов из директории по расширению
def files_name_in_dir(path_name: str, ext: str) -> list:
    return [entry for entry in os.listdir(path_name) if fnmatch.fnmatch(entry, ext)]