import glerbl
import subprocess
import sys
import re
from . import CheckBase

allownonascii = False
try:
    allownonascii = (subprocess.check_output(["git", "config",
                                              "hooks.allownonascii"])
                     .strip() == "true")
except subprocess.CalledProcessError:
    pass

non_ascii_re = re.compile(r"[^ -~]")

class Check(CheckBase):
    """
    Checks that no file with non-ASCII filenames are staged.
    """
    hooks = ["pre-commit"]

    def execute(self, hook):
        if allownonascii:
            return True

        against = glerbl.get_against()

        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only",
             "--diff-filter=A", "-z", against])

        names = output.split("\x00")
        good = True
        for name in [x for x in names if non_ascii_re.search(x) is not None]:
            sys.stderr.write("{0} is a non-ascii file name.".format(name))
            good = False

        return good
