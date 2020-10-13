import sys
from os import listdir
from os.path import isfile, join

class Concatter:

    def __init__(self, folder: str, extension: str, offset: int = 0, end: int = 0, mix_in_file: str = None, mix_in_position: int = -1):
        print('Searching folder:', folder)
        print('Files with extension:', extension)
        self.folder = folder
        self.extension = "." + extension.lower()
        self.offset = offset
        self.end = end
        self.output_filename = join(folder, "output")
        self.mix_in_file = join(folder, mix_in_file + '.' + extension) if mix_in_file else None
        self.mix_in_position = mix_in_position

    def doYourJob(self) -> bool:
        filenames = self.__getFilenames(self.folder, self.extension)

        if self.mix_in_file:
            self.__mix_in_file(self.mix_in_file, self.mix_in_position, filenames)

        if self.end == 0:
            end = len(filenames)
        elif self.end > 0:
            end = self.end
        else:
            end = len(filenames) + self.end

        print('Concat from', self.offset, 'to', end)    
            
        files = filenames[self.offset : end]
        for filename in files:
            print('Concat file:', filename)
            self.__concatFile(self.output_filename, filename)
            
        return True
        
    def __getFilenames(self, folder: str, extension: str) -> [str]:
        filenames = [join(folder, f) for f in listdir(folder) if isfile(join(folder, f)) and f.lower().endswith(extension)]
        filenames.sort()

        return filenames

    def __mix_in_file(self, filename: str, position: int, filenames: [str]) -> None:
        if position > 0:
            filenames.insert(position, filename)

    def __concatFile(self, filename: str, concat_filename: str) -> None:
        with open(filename, "ab") as output_file, open(concat_filename, "rb") as concat_file:
            output_file.write(concat_file.read())

# Main

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Please parse folder containing the files, file extension, offset and end (negative from end, positive from beginning).\n python3 -m concat PATH EXTENSION OFFSET\n e.g. Concat all text files but the last two in folder: python3 -m concat /User/X/files txt -2')
        sys.exit()

    args = sys.argv
    folder = args[1]
    extension = args[2]
    
    offset = 0
    if len(args) >= 4:
        offset = int(args[3])

    end = 0
    if len(args) >= 5:
        end = int(args[4])

    mix_in_file = None
    mix_in_position = -1
    # if len(args) >= 5:
    #     mix_in_file = args[3]
    #     mix_in_position = int(args[4])

    concatter = Concatter(folder, extension, offset, end, mix_in_file, mix_in_position)
    concatter.doYourJob()