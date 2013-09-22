import os
import sys
from . import CheckBase

class Check(CheckBase):
    """
    Checks that there is no BEFORE_COMMIT or BEFORE-COMMIT file in the root
    of the working tree.
    """
    hooks = ["pre-commit"]

    def execute(self, hook):
        if os.environ.get("IGNORE_BEFORE_COMMIT"):
            return True

        ret = True
        if os.path.exists("BEFORE-COMMIT"):
            sys.stderr.write("BEFORE-COMMIT exists.\n")
            ret = False

        if os.path.exists("BEFORE_COMMIT"):
            sys.stderr.write("BEFORE_COMMIT exists.\n")
            ret = False

        return ret
