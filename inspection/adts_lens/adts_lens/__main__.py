from adts_lens.adts_format import AdtsFormat, FrameHeader
import os
from enum import Enum
import sys
from typing import Optional

class AacLens:

    def __init__(self, filename: str):
        self.frame_offsets: [int] = []
        self.data = None
        self.headers = []
        self.handle_file(filename)

    def handle_file(self, filename: str):
        # read file
        with open(filename, 'rb') as file:
            self.data = file.read()

            print('File length:', len(self.data))

            beginning = self.data[0:8]
            print('File begins with:', beginning)
            
            # find frame headers
            self.headers = self.__get_headers(self.data)

    def print_summary(self, log_filename: str = ''):
        log_file = None
        if log_filename:
            log_file = open(log_filename, 'a+')

        message = '----------\n'
        
        message += 'Frame headers: ' + str(len(self.headers)) + '\n'
        
        # check header configs
        multi_aac = list(filter(lambda header: header.aac_frame_count > 1, self.headers))
        message += 'multple aac frames: ' + str(len(multi_aac)) + '\n'
        layers = list(filter(lambda header: header.layer != 0, self.headers))
        message += 'layer != 0: ' + str(len(layers)) + '\n'

        incomplete_frame_count = 0
        new_offset = 0
        for header in self.headers:
            if header.offset != new_offset:
                incomplete_frame_count += 1
            new_offset = header.offset + header.frame_size
        message += 'incomplete frames: ' + str(incomplete_frame_count) + '\n'
        
        print(message)
        
        # write to log file
        if log_file:
            log_file.write(message)

    def print_headers(self, log_filename: str = ''):
        log_file = None
        if log_filename:
            log_file = open(log_filename, 'w')

        if not self.headers:
            print ('No headers found')
            return

        for header in self.headers:
            header.print_me()
            
            # write to log file
            if log_file:
                log_file.write(header.format_string())

    def print_no_headers(self, log_filename: str):
        message = 'No headers found'
        
        if not self.headers:
            print (message)
        
        log_file = None
        if log_filename:
            log_file = open(log_filename, 'w')

        # write to log file
        if log_file:
            log_file.write(message)

    def write_frames(self, path: str, base_filename: str):
        frames_path = '{0}/frames/'.format(path)
        try:
            os.mkdir(frames_path)
        except Exception as _:
            pass

        index = 0
        for header in self.headers:
            filename = '{0}{1}_{2}'.format(frames_path, base_filename, index)
            with open(filename, 'wb') as file:
                file.write(self.data[header.offset : header.offset + header.frame_size])
            index += 1

    # headers
    
    def __get_headers(self, data: bytearray):
        return AdtsFormat.get_all_headers(data)
        
# Main

def main():
    if len(sys.argv) < 5:
        print('Please parse folder containing the file, filename, extension and if separate frames should be written to files.\n python3 -m concat FOLDER FILENAME EXTENSION WRITE_FRAMES\n e.g. python3 -m adts_lens ./files music opus 1')
        sys.exit()

    args = sys.argv
    folder = args[1]
    filename = args[2]
    extension = args[3]
    write_frames = int(args[4])

    # discard extension -> mp3 will be set
    filename = os.path.splitext(filename)[0]

    filepath = '{0}/{1}.{2}'.format(folder, filename, extension)
    log_filepath = '{0}/{1}_log'.format(folder, filename)

    lens = AacLens(filepath)
    lens.print_headers(log_filepath)

    lens.print_summary(log_filepath)

    if write_frames == 1:
        lens.write_frames(folder, filename)

if __name__ == '__main__':
    main()