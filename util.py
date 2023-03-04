import os


def rgb_to_hex(r, g, b):
        return "#%s%s%s" % tuple([hex(c)[2:].rjust(2, "0") for c in (r, g, b)])

def make_paths(paths: tuple|list|str):
    def make(path: str):
        full_path = 'C:\\'

        path_pieces = path.split('\\')
        if path_pieces[-1].find('.') != -1:
            path_pieces.pop()
        if path_pieces[0].find(':') != -1:
            full_path = path_pieces[0]
            path_pieces.pop(0)

        for directory in path_pieces:
            full_path += f"\\{directory}"
            if not os.path.isdir(full_path):
                os.mkdir(full_path)
         
    if type(paths) != str:
        for path in paths:
            make(path)
    else:
        make(paths)
    

