from zipfile import ZipFile
import io


# Из словаря в zip binary
def zip_in_memory(dict_files: dict):
    if dict_files:
        io_data = io.BytesIO()
        zip_file = ZipFile(io_data, 'w')
        fl_add_file = False
        for name_file, data_file in dict_files.items():
            if data_file:
                fl_add_file = True
                zip_file.writestr(name_file, data_file)
        zip_file.close()
        zip_binary = io_data.getvalue()
        io_data.close()
        return zip_binary if fl_add_file else None


if __name__ == '__main__':
    data_test = {
        'file1.txt': b'1234567',
        'file2.txt': b'7654654',
    }
    zip_b = zip_in_memory(data_test)
    with open('test.zip', 'wb') as f:
        f.write(zip_b)
