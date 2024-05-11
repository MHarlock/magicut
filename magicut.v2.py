import os
import argparse
import magic


""" this app is only for cutting file, to take his 'magic number' and 'filename' intact for study how parse mediafile 
information from filename and mime """

class MagiCut:
    def __init__(self):
        self.delete_source = True
        self.overwrite = True
        # self.suffix = ".magicut"
        self.nbytes = 64

    def cutter(self, filename, dest_dir):
        if os.path.isdir(dest_dir):
            if os.path.isfile(filename):
                source_dir = os.path.dirname(filename)

                _, dest_tail_dir = os.path.split(dest_dir)
                tmpname = source_dir
                dest_subdir = ''
                while True:
                    tmpname, tail = os.path.split(tmpname)
                    if tmpname == '' or tmpname == '/' and tail == '' or tail == dest_tail_dir:
                        break
                    dest_subdir = os.path.join(tail, dest_subdir)
                if dest_subdir.strip('/') == source_dir.strip('/') or tmpname == '':
                    _, dest_subdir = os.path.split(os.path.dirname(filename))
                if not os.path.exists(os.path.join(dest_dir, dest_subdir)):
                    os.makedirs(os.path.join(dest_dir, dest_subdir))
                dest_filename = os.path.join(dest_dir, dest_subdir, os.path.basename(filename))
                if os.path.exists(dest_filename):
                    mime_dest = magic.from_file(dest_filename, mime=True)
                else:
                    mime_dest = None
                mimein = magic.from_file(filename, mime=True)
                if mimein == mime_dest:
                    # already present and has same mime
                    return True
                # tmpname = f'{dest_filename}{self.suffix}'
                # if os.path.isfile(tmpname):
                #     os.remove(tmpname)
                mimeout = None
                eof = False
                # return True
                with open(filename, "rb") as fdin:
                    while mimein != mimeout and not eof:
                        fdout = open(dest_filename, "ab")
                        buffer = fdin.read(self.nbytes)
                        if len(buffer) < self.nbytes:
                            eof = True
                        fdout.write(buffer)
                        fdout.close()
                        mimeout = magic.from_file(dest_filename, mime=True)
                fdout.close()
                fdin.close()
                if eof:
                    return False
                # if self.delete_source:
                #     os.remove(filename)
                # if self.overwrite:
                #     os.replace(tmpname, filename)
                print(f'File {filename} cut to {dest_filename}')
                return True
            else:
                print(f'File {filename} not found.')
                return False
        else:
            print(f'Destination Path {dest_dir} is not a directory.')
            return False


if __name__ == '__main__':
    mc_parser = argparse.ArgumentParser()
    mc_parser.add_argument("source_path",
                           help="source_path is source filename or directory. "
                           "If is a directory, all recursive file are Magic Cutted")
    mc_parser.add_argument("dest_path",
                           help="pathname is destination directory. ")

    mc_args = mc_parser.parse_args()
    source_path = mc_args.source_path
    dest_path = mc_args.dest_path
    mc = MagiCut()
    if os.path.isdir(source_path):
        for dirpath, dirnames, filenames in os.walk(source_path):
            for filename in filenames:
                result = mc.cutter(os.path.abspath(f'{dirpath}/{filename}'), os.path.abspath(dest_path))
    elif os.path.isfile(source_path):
        result = mc.cutter(os.path.abspath(f'{source_path}'), os.path.abspath(dest_path))
    else:
        print(f'Invalid source path: {source_path}')
