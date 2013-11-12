import os
import shutil
import subprocess
import atexit
import tempfile

# No warning about globals in this file.
# pylint: disable=W0603

__tmpdir = None

def __clean_tmpdir():
    global __tmpdir
    shutil.rmtree(__tmpdir, ignore_errors=True)
    __tmpdir = None

def get_tmpdir():
    """
    On first invocation, creates a temporary directory and returns its
    path. Subsequent invocations uses the same directory.

    :returns: A temporary directory created for this run of glerbl.
    :rtype: :class:`str`
    """
    global __tmpdir
    if __tmpdir is not None:
        return __tmpdir

    __tmpdir = tempfile.mkdtemp(prefix='.tmp.glerbl.', dir=".")
    atexit.register(__clean_tmpdir)

    return __tmpdir

__cached_against = None

def get_against():
    """
    Determines the revision against which the staged data ought to be checked.

    :returns: The revision.
    :rtype: :class:`str`
    """
    global __cached_against
    if __cached_against is not None:
        return __cached_against

    status = subprocess.call(["git", "rev-parse", "--verify", "HEAD"],
                             stdout=open(os.devnull, 'w'),
                             stderr=subprocess.STDOUT)
    if not status:
        against = 'HEAD'
    else:
	# Initial commit: diff against an empty tree object
        against = '4b825dc642cb6eb9a060e54bf8d69288fbee4904'

    __cached_against = against
    return against


__cached_tree_from_staged = None


def tree_from_staged():
    global __cached_tree_from_staged
    if __cached_tree_from_staged is not None:
        return __cached_tree_from_staged

    against = get_against()

    tmpdir = os.path.join(get_tmpdir(), "tree_from_staged")

    if os.path.exists(tmpdir):
        raise Exception(tmpdir + " already exists")

    os.mkdir(tmpdir)

    # Link all the files that git already knows about.
    for path in subprocess.check_output(["git", "ls-files"],
                                        universal_newlines=True).split("\n"):
        path = path.strip()
        if path == "":
            continue

        dest = os.path.join(tmpdir, path)
        dirname = os.path.dirname(dest)
        if dirname != "" and not os.path.exists(dirname):
            os.makedirs(dirname)

        # Don't try to link to files that don't exist anymore.
        if os.path.exists(path):
            os.link(path, dest)

    # Modify the tree according to what is staged.
    for line in subprocess.check_output(["git", "diff-index", "--cached",
                                         "--full-index", against],
                                        universal_newlines=True).split("\n"):
        line = line.strip()
        if line == "":
            continue

        (_, _, _, sha, status, filename) = line.split()

        dest = os.path.join(tmpdir, filename)
        if os.path.exists(dest):
            if os.path.isdir(dest):
                shutil.rmtree(dest)
            else:
                os.unlink(dest)

        # Deleted file, we're done.
        if status == "D":
            continue

        subprocess.check_call(["git", "cat-file", "-p", sha],
                              stdout=open(dest, 'w'))

    __cached_tree_from_staged = tmpdir
    return tmpdir
