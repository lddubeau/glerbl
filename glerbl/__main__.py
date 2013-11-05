import sys
import argparse
import importlib
import pkgutil
import stat
import os
from six.moves import input

GLERBL_DIR=".glerbl"
prog = None

class Exit(Exception):
    def __init__(self, status):
        super(Exit, self).__init__(status)

class NonExistentConfig(Exception):
    def __init__(self, path):
        super(NonExistentConfig, self).__init__(path)

def fatal(msg):
    sys.stderr.write("{0}: {1}\n".format(prog, msg))
    raise Exit(1)

def error(msg):
    sys.stderr.write("{0}: {1}\n".format(prog, msg))

def __load_config_file(path):
    if not os.path.exists(path):
        raise NonExistentConfig(path)

    glob = {"__file__": path}
    exec(compile(open(path).read(), path, 'exec'), glob)
    return glob

def __load_config():
    local_conf = os.path.join(GLERBL_DIR, "local_conf.py")
    repo_conf = os.path.join(GLERBL_DIR, "repo_conf.py")
    try:
        config = __load_config_file(local_conf)
        if not os.path.exists(repo_conf):
            fatal("{0} exists but not {1}.".format(local_conf, repo_conf))
    except NonExistentConfig:
        try:
            config = __load_config_file(repo_conf)
        except NonExistentConfig:
            fatal("cannot load {0} or {1}.".format(local_conf, repo_conf))
    return config

def __load_checks(check_names):
    checks = []
    for check_name in check_names:
        mod_name = "glerbl.check." + check_name \
                      if check_name.find(".") == -1 else check_name

        try:
            checks.append(importlib.import_module(mod_name))
        except ImportError:
            fatal("cannot import the module for check name {0}."
                  .format(check_name))
    return checks

def __verify_checks_for_hook(checks, hook):
    err = False
    for check in checks:
        if hook not in check.Check.hooks:
            err = True
            error("{0} not among those hooks supported by {1}."
                  .format(hook, check.__name__))
    if err:
        fatal("invalid configuration.")

def _runhook(which):
    config = __load_config()
    checks = __load_checks(config["checks"].get(which, []))
    __verify_checks_for_hook(checks, which)

    failed = False
    for check in checks:
        check_obj = check.Check()
        if not check_obj.execute(which):
            error(check.__name__ + " failed.")
            failed = True

    if failed:
        raise Exit(1)
    raise Exit(0)

def _install(_):
    """
    Install the hooks configured in glerbl.conf.py.

    """
    if not os.path.exists(".git"):
        fatal("not in a git repo.")

    config = __load_config()

    if config.get("checks") is None:
        fatal("global ``checks`` variable missing from configuration.")

    # We try to load all checks to check that they exist NOW.
    for hook in config["checks"]:
        checks = __load_checks(config["checks"][hook])
        # Also verify that they apply to the hooks.
        __verify_checks_for_hook(checks, hook)

    reply = input("This will overwrite your current hooks. "
                  "Proceed [yes/No]? ")
    if reply != "yes":
        raise Exit(0)

    for hook in config["checks"]:
        hook_f = open(os.path.join(".git/hooks/", hook), 'w')
        hook_f.write("""#!/usr/bin/env python
# GENRATED BY GLERBL. DO NOT MODIFY.
from glerbl.__main__ import main


exit(main(["glerbl", "hook", "{0}"]))
""".format(hook))
        os.fchmod(hook_f.fileno(),
                  os.fstat(hook_f.fileno()).st_mode | stat.S_IXUSR)
        hook_f.close()

def _listchecks(_):
    """
    Outputs to stdout the list of checks that glerbl knows about. The
    format of the list is::

        module_name [list of hooks]

           docstring

    The identifier ``module_name`` is the name of the module
    implementing the check. This name is how you'd refer to the check
    in your ``glerbl.conf.py`` file. The ``[list of hooks]`` is a list
    of hook name to which this check can be applied. The ``docstring``
    is a description of what the hook does.

    """
    import glerbl.check
    package = glerbl.check
    for _, modname, _ in pkgutil.walk_packages(path=package.__path__):
        mod = importlib.import_module(package.__name__+ '.' + modname)
        print(modname, mod.Check.hooks)
        print(mod.Check.__doc__)

def main(args=None):
    try:
        if args is None:
            args = sys.argv
        global prog # pylint: disable=W0603
        prog = sys.argv[0]
        if args and args[1] == "hook":
            if len(args) != 3:
                fatal("hook command requires 2 arguments.")
            _runhook(args[2])

        parser = argparse.ArgumentParser('Glerbl')
        subparsers = parser.add_subparsers(title="subcommands",
                                           help="subcommand")

        install_sp = subparsers.add_parser(
            "install",
            description=_install.__doc__,
            help="installs glerbl",
            formatter_class=argparse.RawTextHelpFormatter)
        install_sp.set_defaults(func=_install)

        listcheck_sp = subparsers.add_parser(
            "listchecks",
            description=_listchecks.__doc__,
            help="lists the checks that glerbl knows",
            formatter_class=argparse.RawTextHelpFormatter)
        listcheck_sp.set_defaults(func=_listchecks)

        args = parser.parse_args()

        args.func(args)
    except Exit as e:
        return e.args[0]
    return 0

if __name__ == '__main__':
    exit(main())
