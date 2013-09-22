import subprocess
import os
import sys

import glerbl
from . import CheckBase

class Check(CheckBase):
    """
    Checks that non of the staged files have PEP8 errors. It runs the
    ``pep8`` tool on all the stages files.
    """

    hooks = ["pre-commit"]

    def execute(self, hook):
        against = glerbl.get_against()

        fail = False

        for line in subprocess.check_output(["git", "diff-index", "--cached",
                                             "--full-index", against],
                                            universal_newlines=True) \
                              .split("\n"):
            line = line.strip()
            if line == "":
                continue

            (_, _, _, sha, status, filename) = line.split()

            ext = os.path.splitext(filename)[1]

            if ext != ".py" or status == "D":
                continue

            pep_ret = os.system(("git cat-file -p {0} | "
                                "pep8 /dev/stdin > /dev/null").format(sha))
            if pep_ret != 0:
                sys.stderr.write(filename + " does not comply with pep8.\n")
                fail = True

        if fail:
            return False
        return True
