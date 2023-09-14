import os
import shutil
import json
from unidecode import unidecode
import sys


class FileOrganizer:
    def __init__(self, path, extensions_file_path='file_extensions.json'):
        self.path = path
        with open(extensions_file_path, 'r') as file:
            self.dict_of_extensions = json.load(file)

        self.folder_to_ignore = [key for key in self.dict_of_extensions.keys()]

    def normalize(self, name):
        name = unidecode(name)
        name, extension = name.split('.')
        new_name = ''.join(char if char.isalnum() else '_' for char in name)
        return new_name, extension

    def process_folders(self):
        self.create_folders()
        self.move_files()
        self.remove_folders()
        self.unpack_archives()

    def create_folders(self):
        for folder_exists in self.folder_to_ignore:
            path = os.path.join(self.path, folder_exists)
            if not os.path.exists(path):
                os.makedirs(path)

    def move_files(self):
        for root, dirs, files in os.walk(self.path, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.folder_to_ignore]

            for file in files:
                found = False
                new_file_name, extension = self.normalize(file)
                for key, value in self.dict_of_extensions.items():
                    if extension.upper() in value:
                        found = True
                        old_path = os.path.join(root, file)
                        new_path = os.path.join(self.path, key, f'{new_file_name}.{extension}')
                        shutil.move(old_path, new_path)
                        break

                if not found:
                    new_path = os.path.join(self.path, 'rest', f'{new_file_name}.{extension}')
                    old_path = os.path.join(root, file)
                    shutil.move(old_path, new_path)

    def remove_folders(self):
        for root, dirs, files in os.walk(self.path, topdown=True):
            for folder in dirs:
                if folder not in self.folder_to_ignore:
                    shutil.rmtree(os.path.join(root, folder))

    def unpack_archives(self):
        for root, dirs, files in os.walk(os.path.join(self.path, 'archives')):
            for file in files:
                file_name, extension = self.normalize(file)
                if extension.upper() in self.dict_of_extensions['archives']:
                    old_path = os.path.join(root, file)
                    new_path = os.path.join(root, file_name)
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    try:
                        shutil.unpack_archive(old_path, new_path, extension)
                    except Exception as e:
                        print(f"Error unpacking file '{file}': {e}")
                    else:
                        os.remove(old_path)
                else:
                    print(f"File '{file}' is not a recognized archive format")


def main():
    folder_to_sort = sys.argv[1]
    organizer = FileOrganizer(folder_to_sort)
    organizer.process_folders()
