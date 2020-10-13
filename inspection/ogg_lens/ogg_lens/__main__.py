from ogg_lens.ogg_format import OggFormat, PageHeader
from ogg_lens.opus_format import OpusFormat, PacketHeader
import os
from enum import Enum
import sys
from typing import Optional

class Format(Enum):
    OGG_BITSTREAM = 0
    OPUS_PACKET = 1
    # VORBIS_PACKET = 2

class OggLens:

    def __init__(self, filename: str, format: Format):
        self.format = format
        self.frame_offsets: [int] = []
        self.data = None
        self.codec_header = None
        self.handle_file(filename)

    def handle_file(self, filename: str):
        # read file
        with open(filename, 'rb') as file:
            self.data = file.read()

            beginning = self.data[0:8]
            print('File begins with:', beginning)
            
            # find page headers
            self.headers = self.__get_headers(self.data)

            # print codec
            self.__get_codec(self.data)

    def print_summary(self, log_filename: str = ''):
        log_file = None
        if log_filename:
            log_file = open(log_filename, 'a+')

        message = '----------\n'
        
        if self.codec_header:
            message += 'Codec header:\n'
            message += self.codec_header.format_string(False)
            message += '----------\n'


        if self.codec_header:
            message += 'Codec: ' + self.codec_header.get_codec_name() + '\n'
        
        message += 'Page headers: ' + str(len(self.headers)) + '\n'
        
        # tags
        second_page_segment_offset = OggFormat.get_first_segment_offset(self.headers[1])
        message += 'Second page is OpusTags: ' + str(OpusFormat.is_magic_structure_tags(self.data, second_page_segment_offset)) + '\n'

        # check header configs
        fresh = list(filter(lambda header: header.is_fresh == True, self.headers))
        message += 'fresh headers: ' + str(len(fresh)) + '\n'
        bos = list(filter(lambda header: header.is_bos == True, self.headers))
        message += 'bos headers: ' + str(len(bos)) + '\n'
        eos = list(filter(lambda header: header.is_eos == True, self.headers))
        message += 'eos headers: ' + str(len(eos)) + '\n'

        # check page numbers
        first_missing_page_num = -1
        current_page_num = -1
        for header in self.headers:
            if header.page_num != current_page_num + 1:
                first_missing_page_num = current_page_num + 1
                break
            current_page_num = header.page_num
        message += 'First missing page number: ' + str(first_missing_page_num) + '\n'

        is_page_numbers_increasing = True
        current_page_num = -1
        for header in self.headers:
            if header.page_num < current_page_num:
                is_page_numbers_increasing = False
                break
            current_page_num = header.page_num
        message += 'Is page number contantely increasing: ' + str(is_page_numbers_increasing) + '\n'

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
        if self.format == Format.OPUS_PACKET:
            print('Write frames not implemented for OPUS_PACKET.')
            return

        frames_path = '{0}/frames/'.format(path)
        try:
            os.mkdir(frames_path)
        except Exception as _:
            pass

        index = 0
        for header in self.headers:
            filename = '{0}{1}_{2}'.format(frames_path, base_filename, index)
            with open(filename, 'wb') as file:
                file.write(self.data[header.offset : header.offset + header.page_size])
            index += 1

    # headers
    
    def __get_headers(self, data: bytearray):
        bitstream_headers = OggFormat.get_all_headers(data)
        # for header in bitstream_headers:
        #     print("Found bitstream header at", header.offset)

        if self.format == Format.OGG_BITSTREAM:
            return bitstream_headers
        elif self.format == Format.OPUS_PACKET:
            return OpusFormat.get_all_headers(data)

    def __get_codec(self, data: bytearray):
        if not self.headers:
            print("Can't identify codec. No headers.")

        id_header = self.headers[0]
        if not id_header.segment_size_table:
            print("Can't identify codec. No segmentes in id header.")

        codec_segment_size = id_header.segment_size_table[0]
        if codec_segment_size >= PacketHeader.HEADER_SIZE:
            if OpusFormat.is_magic_structure(data, PageHeader.HEADER_SIZE):
                header = OpusFormat.get_header(data, PageHeader.HEADER_SIZE)
                if header:
                    self.codec_header = header
        
# Main

def main():
    if len(sys.argv) < 5:
        print('Please parse folder containing the file, filename, extension and if separate frames should be written to files.\n python3 -m concat FOLDER FILENAME EXTENSION WRITE_FRAMES\n e.g. python3 -m ogg_lens ./files music opus 1')
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

    format = Format.OGG_BITSTREAM

    lens = OggLens(filepath, format)
    lens.print_headers(log_filepath)

    lens.print_summary(log_filepath)

    if write_frames == 1:
        lens.write_frames(folder, filename)

if __name__ == '__main__':
    main()