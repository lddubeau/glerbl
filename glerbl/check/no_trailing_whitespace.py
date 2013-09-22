import glerbl
import subprocess
from . import CheckBase

class Check(CheckBase):
    """
    Checks that none of the staged files contain trailing whitespaces.
    """
    hooks = ["pre-commit"]

    def execute(self, hook):
        against = glerbl.get_against()
        st = subprocess.call(["git", "diff-index", "--check", "--cached",
                              against, "--"],
                             stderr=subprocess.STDOUT)
        if st != 0:
            return False
        return True
