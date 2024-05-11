import os
import argparse
import magic


""" this app is only for cutting file, to take his 'magic number' and 'filename' intact for study how parse mediafile 
information from filename and mime """

class MagiCut:
    def __init__(self):
        self.delete_source = True
        self.overwrite = True
        self.suffix = ".magicut"
        self.nbytes = 64

    def cutter(self, filename):
        if os.path.isfile(filename):
            tmpname = f'{filename}{self.suffix}'
            if os.path.isfile(tmpname):
                os.remove(tmpname)
            mimein = magic.from_file(filename, mime=True)
            mimeout = None
            eof = False
            with open(filename, "rb") as fdin:
                while mimein != mimeout and not eof:
                    fdout = open(tmpname, "ab")
                    buffer = fdin.read(self.nbytes)
                    if len(buffer) < self.nbytes:
                        eof = True
                    fdout.write(buffer)
                    fdout.close()
                    mimeout = magic.from_file(tmpname, mime=True)
            fdout.close()
            fdin.close()
            if eof:
                return False
            if self.delete_source:
                os.remove(filename)
            if self.overwrite:
                os.replace(tmpname, filename)
            print(f'File {filename} cut to {tmpname}')
            return True
        else:
            print(f'File {filename} not found.')
            return False


if __name__ == '__main__':
    mc_parser = argparse.ArgumentParser()
    mc_parser.add_argument("pathname", help="pathname is filename or directory. "
                                            "If is a directory, all recursive file are Magic Cutted")
    mc_args = mc_parser.parse_args()
    pathname = mc_args.pathname
    mc = MagiCut()
    if os.path.isdir(pathname):
        for dirpath, dirnames, filenames in os.walk(pathname):
            for filename in filenames:
                result = mc.cutter(os.path.abspath(f'{dirpath}/{filename}'))
    elif os.path.isfile(pathname):
        result = mc.cutter(os.path.abspath(f'{pathname}'))
    else:
        print(f'Invalid pathname: {pathname}')
