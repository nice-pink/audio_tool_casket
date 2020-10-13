from glob import glob
import os
from file_dealer.lib.utils.log import Log

class Cook:

    def __init__(self, location: str, file_type: str):
        self.file_index = 0
        self.files = self.__get_files(location) if not file_type else self.__get_files_of_type(location, file_type)

    def get_next_packet(self):
        if self.file_index < len(self.files):
            packet = self.files[self.file_index]
            self.file_index += 1
            return packet
        else:
            return None

    # Get files from folder

    def __get_files(self, location: str):
        location_fixed = self.__fix_location(location)
        search = '{0}/*'.format(location_fixed)
        filenames = glob(search, recursive=False)
        Log.info(filenames)
        return filenames

    def __get_files_of_type(self, location: str, file_type: str) -> [str]:
        files = []
        for path, _, filenames in os.walk(location):
            filenames.sort()
            for filename in filenames:
                if file_type in filename:
                    files.append(os.path.join(path, filename))
        Log.info(files)
        return files
        
        # location_fixed = self.__fix_location(location)
        # search = '{0}/*.{1}'.format(location_fixed, file_type)
        # filenames = glob(search, recursive=False)
        # Log.info(filenames)
        # return filenames

    # Slice file in packets

    # def get_packets_from_file(self, filepath: str):
    #     return []

    # Helper

    def __fix_location(self, location: str) -> str:
        if location.endswith('/'):
            return location[:-1]