from mp3_lens.mp3_format import Mp3Format
from mp3_lens.idv3_format import IdV3TagFormat, TagRange
import os
import sys

class Mp3Surgeon:

    def __init__(self, filename: str):
        self.frame_offsets: [int] = []
        self.data = None
        
        # read file
        with open(filename, 'rb') as file:
            self.data = file.read()

            # find id v3 tag size
            self.tag_range = IdV3TagFormat.get_id_v3_tag_range(self.data)
            
            frame_offset = 0
            if self.tag_range.size > 0:
                frame_offset = self.tag_range.offset + self.tag_range.size

            # find frame offsets
            self.__find_frame_offsets(self.data, frame_offset)
        
        # set first header as source of truth
        self.first_header = Mp3Format.get_mpeg_header(self.data, self.frame_offsets[0])

    def print_headers(self, log_filename: str = ''):
        headers = self.__get_headers()
        
        log_file = None
        if log_filename:
            log_file = open(log_filename, 'w')

        index = 0
        for header in headers:
            header.print_me(self.first_header, index)
            index += 1
            
            # write to log file
            if log_file:
                log_file.write(header.format_string(self.first_header, index))

        # Id V3 tag

        id_v3_str = '\n\nFound Id V3 Tag at position: {0} with size: {1}'.format(str(self.tag_range.offset), str(self.tag_range.size))
        if log_file:
            log_file.write(id_v3_str)
    
        print(id_v3_str)

        first_frame_offset = headers[0].offset
        if Mp3Format.is_info_frame(self.data, first_frame_offset):
            info_str = '\n\nHas Info frame. LAME tag {0}.'.format(Mp3Format.get_lame_tag(self.data, first_frame_offset))
            if log_file:
                log_file.write(info_str)
    
            print(info_str)

        if Mp3Format.is_xing_frame(self.data, first_frame_offset):
            info_str = '\n\nHas Xing frame. LAME tag {0}.'.format(Mp3Format.get_lame_tag(self.data, first_frame_offset))
            if log_file:
                log_file.write(info_str)
    
            print(info_str)

    def write_data(self, path: str, base_filename: str, as_block: bool = False, write_tags: bool = False):
        frames_path = '{0}/frames/'.format(path)
        try:
            os.mkdir(frames_path)
        except Exception as _:
            pass

        if write_tags :
            self.__write_tags(frames_path, base_filename)

        self.__write_frames(frames_path, base_filename, as_block)

    def __write_frames(self, path: str, base_filename: str, as_block: bool = False):
        headers = self.__get_headers()
        leading_zeros = 5

        # skip Info or Xing frame
        index_of_first_audio_frame = self.__get_first_audio_frame_index(self.data, headers)

        # write a single block containing all frames
        if as_block:
            first_offset = headers[index_of_first_audio_frame].offset
            filename = '{0}{1}_block.mp3'.format(path, base_filename)
            with open(filename, 'wb') as file:
                file.write(self.data[first_offset: len(self.data)])
            return

        # write each frame in single file
        index = 0
        prior_header = headers[index_of_first_audio_frame]
        for header in headers[index_of_first_audio_frame + 1:]:
            file_number = str(index).zfill(leading_zeros)
            filename = '{0}{1}_{2}.mp3'.format(path, base_filename, file_number)
            
            # with open('files/sizes', 'a') as file:
            #     size = header.offset - prior_header.offset
            #     file.write(str(index) + ': ' + str(size) + '\n')
            
            with open(filename, 'wb') as file:
                file.write(self.data[prior_header.offset: header.offset])
            index += 1
            prior_header = header

        # write last header
        if index > 0:
            file_number = str(index).zfill(leading_zeros)
            filename = '{0}{1}_{2}.mp3'.format(path, base_filename, file_number)
            last_header = headers[-1]
            with open(filename, 'wb') as file:
                file.write(self.data[last_header.offset: len(self.data)])
            
    def __write_tags(self, path: str, base_filename: str):
        if self.tag_range.size > 0:
            filename = '{0}_{1}_tag.mp3'.format(path, base_filename)
            with open(filename, 'wb') as file:
                file.write(self.data[self.tag_range.offset : self.tag_range.offset + self.tag_range.size])

    # frames

    def __find_frame_offsets(self, data: bytearray, initial_offset: int = 0):
        offset = initial_offset
        frame_size = 0
        
        while offset + frame_size < len(data):
            offset = self.__get_next_frame_index(data, offset)
            if offset < 0:
                break
            
            frame_size = Mp3Format.get_frame_size(data, offset)
            
            if frame_size > 0:
                self.frame_offsets.append(offset)
            else:
                frame_size = 1

            offset += frame_size

    def __get_next_frame_index(self, data: bytearray, offset: int) -> int:
        while offset < len(data):
            if Mp3Format.is_sync_header(data, offset):
                return offset
            offset += 1
        return -1

    def __get_first_audio_frame_index(self, data: bytearray, headers: []) -> int:
        first_header = headers[0]
        if Mp3Format.is_info_frame(data, first_header.offset) or Mp3Format.is_xing_frame(data, first_header.offset):
            return 1
        return 0

    # headers
    
    def __get_headers(self):
        headers = []
        for offset in self.frame_offsets:
            header = Mp3Format.get_mpeg_header(self.data, offset)
            if header:
                headers.append(header)
        return headers

# Main

def main():
    # FILENAME = 'test_copy'
    # PATH = './files'

    if len(sys.argv) < 4:
        print('Please parse folder containing the file, filename and if separate frames should be written to files.\n python3 -m mp3_lens FOLDER FILENAME WRITE_FRAMES\n e.g. python3 -m mp3_lens ./files music 1')
        sys.exit()

    args = sys.argv
    folder = args[1]
    filename = args[2]
    write_frames = int(args[3])

    # discard extension -> mp3 will be set
    filename = os.path.splitext(filename)[0]

    filepath = '{0}/{1}.mp3'.format(folder, filename)
    log_filename = '{0}/{1}_log'.format(folder, filename)

    surgeon = Mp3Surgeon(filepath)
    surgeon.print_headers(log_filename)

    if write_frames == 1:
        surgeon.write_data(folder, filename, as_block=False)

if __name__ == '__main__':
    main()