#!/usr/bin/python3
import os
import shutil
import argparse
import magic


""" this app is only for cutting file, to take his 'magic number' and 'filename' intact for study how parse mediafile 
information from filename and mime """

class bcolors:  # class for print colored on ANSI terminal
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MagiCut:
    def __init__(self, source=None, destination=None, delete=False, overwrite=False, rename=True):

        self.col, self.row = shutil.get_terminal_size(fallback=(0, 0)) # os.get_terminal_size()
        if self.col == 0 or self.row == 0:
            print(f'This is not a terminal!!')
        if source is None and destination is None:
            mc_parser = argparse.ArgumentParser()
            mc_parser.add_argument("source",
                                   help="source is source filename or directory. "
                                        "If is a directory, all recursive file are Magic Cutted")
            mc_parser.add_argument("destination_path",
                                   help="pathname is destination directory. ")

            mc_parser.add_argument("-d", '--delete', action="store_true", required=False,
                                   default=None, help="delete source when successful!")
            mc_parser.add_argument("-o", '--overwrite', action="store_true", required=False,
                                   default=None, help="overwrite destination if already exist.")
            mc_parser.add_argument("-r", '--rename', action="store_true", required=False,
                                   default=None, help="automatic rename destination if already exists.")

            mc_args = mc_parser.parse_args()

            source = os.path.abspath(mc_args.source)
            destination = mc_args.destination_path

            delete = delete if mc_args.delete is None else mc_args.delete
            overwrite = overwrite if mc_args.overwrite is None else mc_args.overwrite
            rename = rename if mc_args.rename is None else mc_args.rename

        if not os.path.isdir(destination):
            print(f'Destination path "{destination}" must be a directory.')
            exit(2)
        # delete source after a valid generation of .magicut file
        self.delete = delete
        # overwrite destination file if already exist
        self.overwrite = overwrite
        self._tmp_Overwrite = False  # temporary Overwrite if destination file exist and has different mime
        # if not self.overwrite set as rename (not overwrite and not rename means skip don't save)
        self.rename = rename if not overwrite else False

        self.suffix = ".magicut"
        self.nbytes = 64

        destination = os.path.abspath(destination)
        self.dest_path = destination

        if os.path.exists(source):
            if os.path.isfile(source):
                self.filename = os.path.abspath(os.path.basename(source))
                self.source_path = os.path.dirname(source)
            else:
                self.filename = ''
                self.source_path = os.path.abspath(source)
            os.chdir(self.source_path)
            print(f'CWD: {os.getcwd()}')
        else:
            raise FileNotFoundError(source)
        print(f'__init__ source: {source} - self.source: {self.source_path} - filename: {self.filename}')
        self.same = self.isSame(self.source_path, self.dest_path)

    def isSame(self, source: str, dest: str):
        if os.path.exists(source) and os.path.exists(dest):
            return os.path.samefile(source, dest) and str(source).strip("/") == str(dest).strip("/")
        else:
            if source.rstrip('/') == dest.rstrip('/'):
                return True
        return False

    def make_path(self, source, dest) -> str:
        if os.path.isfile(dest):
            raise Exception(f'Destination path "{dest}" is not a directory.')
        else:
            _, tail = os.path.split(dest)
            src_tmp = source
            subdir = ''
            while True:
                src_tmp, src_tail = os.path.split(src_tmp)
                if src_tmp == '' or src_tail == tail:
                    break
                if src_tmp == '/' and src_tail == '':
                    subdir = os.path.join('/', subdir)
                    break
                subdir = os.path.join(str(src_tail), subdir)
            # if source and subdir are same path means there isn't a common piece of path or single dirname
            # between source and dest so only last dirname of source will be added to destination path
            if self.isSame(subdir, source) or src_tmp == '':  # instead os.path.samefile()
                _, subdir = os.path.split(source)
            if not os.path.exists(os.path.join(dest, subdir)):
                os.makedirs(os.path.join(dest, subdir))
            print(f'make_path: src_tmp: {src_tmp} - tail:{tail}\n           dest: {dest} - subdir: {subdir}')
            input("wait enter to continue ...")
            return os.path.join(str(dest), subdir)

    def cut(self, source_path, source_file, dest_path):  # source_file = source full pathname; dest_file o dest_path ?
        source = os.path.join(source_path, source_file)
        dest = os.path.join(self.make_path(source_path, dest_path), source_file)
        if len(dest) > (self.col - 12):
            pdest = f'{dest[:int((self.col-12)/2)-4]}...{dest[-(int((self.col-12)/2)-4):]}'
        else:
            pdest = dest
        source_mime = magic.from_file(source, mime=True)
        if self.overwrite != self.rename:  # when only one (exclusive or XOR) is True
            dest_mime = None
        else:  # overwrite and rename are both False (skip o tmp_Overwrite)
            # or both True (error condition but should be bypassed by self.rename declaration in __init__)
            if os.path.exists(dest):
                dest_mime = magic.from_file(dest, mime=True)
                if source_mime == dest_mime:  # and not self.overwrite and not self.rename
                    # skip, not overwrite and not rename means skip don't save
                    print(f'{bcolors.WARNING}Skip good "{pdest}"')
                    return ''
                self._tmp_Overwrite = True
            dest_mime = None

        dest_tmp = f'{dest}{self.suffix}'
        fdout = open(dest_tmp, "wb")
        fdout.close()
        buffer = 'start'
        with open(source, "rb") as fdin:
            while source_mime != dest_mime and len(buffer) > 0:  # buffer should be nbytes
                fdout = open(dest_tmp, "ab")
                buffer = fdin.read(self.nbytes)
                fdout.write(buffer)
                fdout.close()
                dest_mime = magic.from_file(dest_tmp, mime=True)
        print(f'{bcolors.OKGREEN}Add new > "{pdest}"')
        if source_mime == dest_mime:  # don't care about size but only if are same mime
            return dest_tmp
        else:
            return ''

    def save_dest_file(self, destination):
        dest_pathname, suffix = os.path.splitext(destination)
        if suffix == self.suffix:
            if os.path.exists(dest_pathname):
                if os.path.isfile(dest_pathname):
                    if self.overwrite or self._tmp_Overwrite:
                        self._tmp_Overwrite = False
                        return os.replace(destination, dest_pathname)
                    elif self.rename:
                        num = 0
                        name, ext = os.path.splitext(dest_pathname)
                        dest_new_pathname = dest_pathname
                        while os.path.exists(dest_new_pathname):
                            dest_new_pathname = f'{name}.{str(num).strip()}{ext}'
                            num += 1
                        return os.replace(destination, dest_new_pathname)
                    else:
                        print(f'Destination "{dest_pathname}" already exist and '
                              f'you have chosen not to overwrite or rename.')
                else:
                    raise FileExistsError(f'Destination "{dest_pathname}" already exist and is a directory.')
            else:
                return os.replace(destination, dest_pathname)

    def cutter(self):

        print(f'magicut Start, terminal size ({self.col}, {self.row})')
        if self.filename:
            self.cut(self.source_path, self.filename, self.dest_path)
        else:
            for dirpath, _, filenames in os.walk(self.source_path):
                for filename in filenames:
                    destination = self.cut(dirpath, filename, self.dest_path)
                    if destination:
                        self.save_dest_file(destination)
                        pass
                        if self.delete:
                            os.remove(os.path.join(dirpath, filename))
        print(f'magicut End!')


if __name__ == '__main__':
    try:
        mc = MagiCut(rename=False)
        mc.cutter()
    except FileNotFoundError as fnf:
        print(f'Source "{fnf.args[0]}" doesn\'t exist.\n{fnf.args}')
        exit(1)
    except Exception as err:
        print(f'Error {err}')
        exit(255)

    pass
    print(f'{bcolors.ENDC}')