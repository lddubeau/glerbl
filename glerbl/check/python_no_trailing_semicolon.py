import glerbl
import subprocess
import os
import sys
from . import CheckBase

class Check(CheckBase):
    """
    Checks that no Python file among those staged contain a trailing
    semicolon. Pylint is used for this check. So if you run a more
    comprehensive pylint check, you might want to skip this check and
    have your other check include the semicolon check.
    """
    hooks = ["pre-commit"]

    def execute(self, hook):
        against = glerbl.get_against()
        tmpdir = glerbl.tree_from_staged()

        fail = 0

        for line in subprocess.check_output(["git", "diff-index", "--cached",
                                             "--full-index", against],
                                            universal_newlines=True).split("\n"):
            line = line.strip()
            if line == "":
                continue

            (_, _, _, _, status, filename) = line.split()

            ext = os.path.splitext(filename)[1]

            if ext != ".py" or status == "D":
                continue

            stdout = open(os.devnull, 'w')
            lint_st = subprocess.call(["pylint", "--disable=E,C,W,R",
                                       "--enable=W0301",
                                       os.path.join(tmpdir, filename)],
                                      stdout=stdout)
            if lint_st != 0:
                sys.stderr.write(filename +
                                 " contains trailing semicolons; or was so "
                                 "mangled that pylint failed.\n")
                fail = True

        if fail:
            return False

        return True
