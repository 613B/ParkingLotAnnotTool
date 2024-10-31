import os
import os.path as osp
import shutil
from glob import glob

def remove_if_exists(p):
    if osp.exists(p):
        if osp.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)

def ext(path):
    return osp.splitext(path)[1]

def chext(path, ext):
    return osp.splitext(path)[0] + ext

def isext(path, ext):
    if type(ext) is str:
        return osp.splitext(path)[1] == ext
    if type(ext) in [list, tuple]:
        return osp.splitext(path)[1] in ext

def list_files(path):
    return [osp.join(path, p) for p in os.listdir(path) if osp.isfile(osp.join(path, p))]

def list_folders(path):
    return [osp.join(path, p) for p in os.listdir(path) if osp.isdir(osp.join(path, p))]

def list_by_ext(path, ext, recursive=False):
    if recursive:
        wildcard = osp.join('**', '*')
    else:
        wildcard = '*'
    if type(ext) is str:
        return glob(osp.join(path, f'{wildcard}{ext}'), recursive=recursive)
    paths = []
    for _ext in ext:
        paths += glob(osp.join(path, f'{wildcard}{_ext}'), recursive=recursive)
    return paths
