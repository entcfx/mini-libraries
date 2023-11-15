# A custom implementation of the shutil module
import os

def copy(src, dest):
    """Copy a file or directory to another location."""

    # Helper functions for copy()
    def _copyfileobj(fsrc, fdest):
        with open(fsrc, 'rb') as fsrc:
            with open(fdest, 'wb') as fdest:
                while True:
                    buf = fsrc.read(8192)
                    if not buf:
                        break
                    fdest.write(buf)
    def _copytree(src, dst):
        names = os.listdir(src)
        os.makedirs(dst)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                _copytree(srcname, dstname)
            else:
                _copyfileobj(srcname, dstname)
    
    if not src:
        raise ValueError('source must be specified')
    if not dest:
        raise ValueError('destination must be specified')
    if os.path.isdir(src):
        return _copytree(src, dest)
    else:
        return _copyfileobj(src, dest)

def copytree(src, dst):
    """Copies a tree of files from src to the dst"""
    names = os.listdir(src)
    os.makedirs(dst)
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        if os.path.islink(srcname):
            linkto = os.readlink(srcname)
            os.symlink(linkto, dstname)
        elif os.path.isdir(srcname):
            copytree(srcname, dstname)
        else:
            copy._copyfileobj(srcname, dstname)

def rmtree(path):
    """Removes a tree of files using the OS library"""
    names = os.listdir(path)
    for name in names:
        path = os.path.join(path, name)
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.remove(path)
    os.rmdir(path)

def move(src, dst):
    """Moves a file or a folder (and all its contents) to a different place
    Is implemented by coping and then deleting the original"""
    copytree(src, dst)
    rmtree(src)

def remove(path):
    """Remove a single file or empty folder."""
    if os.path.exists(path):
        if os.path.isdir(path):
            try:
                os.rmdir(path)
            except OSError:
                raise SystemError(f'Error removing directory: {path}')
        else:
            os.unlink(path)
    else:
        raise SystemError(f'Path does not exist: {path}')

def mkdir(path):
    """Create a new directory at the specified location."""
    os.mkdir(path)

def mkdirs(path):
    """Creates directories recursively for the given path."""
    os.makedirs(path)

def exists(path):
    return os.path.exists(path)

def getsize(path):
    """Get the size of a file in bytes."""
    return os.path.getsize(path)

def rename(src, dst):
    """Rename a file or directory."""
    os.rename(src, dst)
