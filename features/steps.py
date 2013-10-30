# -*- coding: utf-8 -*-
import contextlib
import sys
import os
import shutil
import tempfile
from glerbl.__main__ import main
import subprocess
import multiprocessing
import fcntl
import time

from freshen import * # pylint: disable=W0401,W0614
from freshen.checks import * # pylint: disable=W0401,W0614

def set_nonblocking(fd):
    flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def glerbl_func(args, stdin, stdout, stderr):
    sys.stdin = os.fdopen(stdin, 'r')
    sys.stdout = os.fdopen(stdout, 'w')
    sys.stderr = os.fdopen(stderr, 'w')
    sys.argv = args
    ret = main()
    sys.stdin.flush()
    sys.stdout.flush()
    sys.stderr.flush()
    exit(ret)

def start_glerbl(args):
    (stdin_r, stdin_w) = os.pipe()
    (stdout_r, stdout_w) = os.pipe()
    (stderr_r, stderr_w) = os.pipe()
    ret = multiprocessing.Process(target=glerbl_func,
                           args=[args, stdin_r, stdout_w, stderr_w])
    ret.start()
    os.close(stdin_r)
    os.close(stdout_w)
    os.close(stderr_w)
    set_nonblocking(stdout_r)
    set_nonblocking(stderr_r)
    return (ret, os.fdopen(stdin_w, 'w'), os.fdopen(stdout_r, 'r'),
            os.fdopen(stderr_r, 'r'))

def git(repo, *args):
    subprocess.check_call(args, cwd=repo)

@contextlib.contextmanager
def chdir(to):
    pwd = os.getcwd()
    os.chdir(to)
    yield to
    os.chdir(pwd)

@contextlib.contextmanager
def temp_dir():
    tmpdir = tempfile.mkdtemp(dir="features")
    yield tmpdir
    shutil.rmtree(tmpdir)

@contextlib.contextmanager
def temp_chdir():
    with temp_dir() as tmpdir:
        with chdir(tmpdir):
            yield tmpdir

@After
def after(_):
    if scc.repo is not None:
        shutil.rmtree(scc.repo)

@Given("^a non-git directory$")
def non_git():
    scc.repo = tempfile.mkdtemp(dir="features")

@Given("^a git repository$")
def git_step():
    scc.repo = tempfile.mkdtemp(dir="features")
    git(scc.repo, "git", "init", "-q")

@Given("^a configuration that does not have the checks variable$")
def config_without_checks():
    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w').close()

@Given("^a local_conf.py file$")
def local_conf():
    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    open(os.path.join(scc.repo, ".glerbl", "local_conf.py"), 'w').close()

@Given("^a configuration that refers to a non-existent check$")
def config_with_non_existent_check():
    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    with open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w') as \
         conf:
        conf.write("checks = {'pre-commit': ['nonexistent']}\n")

@Given("^a configuration that refers to a check for the wrong hook$")
def config_with_check_for_wrong_hook():
    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    with open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w') as \
         conf:
        conf.write("checks = {'post-commit': ['no_before_commit']}\n")

@Given("^a correct configuration$")
def correct_configuration():
    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    with open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w') as \
         conf:
        conf.write("checks = {'pre-commit': ['no_before_commit']}\n")

@Given("^a staged file$")
def a_staged_file():
    foo = os.path.join(scc.repo, "foo")
    with open(foo, 'w'):
        pass
    git(scc.repo, "git", "add", "foo")

@Given(r"^a git repository in which (\w+ is|no checks are) to be run$")
def git_repo_in_with_x(check):
    run_steps("Given a git repository")
    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    with open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w') as \
         conf:
        conf.write("checks = {{{0}}}\n"
                   .format("" if check == "no checks are"
                           else ("'pre-commit': ['{0}']".format(check[0:-3]))))

    run_steps("""
    When the user installs glerbl
    And answers affirmatively the install prompt
    """)
    scc.proc.join()
    assert_equal(scc.proc.exitcode, 0)
    # These have become useless
    del scc.proc
    del scc.stdin
    del scc.stderr
    del scc.stdout


@When(r"^the user removes all checks$")
def user_removes_all_checks():
    with open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w') as \
         conf:
        conf.write("checks = {}\n")


@Given(r"^a git repository in which all pre-commit checks are to be run$")
def git_repo_in_with_all_pre_commit():
    run_steps("Given a git repository")
    checks = []
    for module in os.listdir("glerbl/check"):
        (name, ext) = os.path.splitext(module)
        if not name.startswith("_") and ext == ".py":
            checks.append(name)

    os.mkdir(os.path.join(scc.repo, ".glerbl"))
    with open(os.path.join(scc.repo, ".glerbl", "repo_conf.py"), 'w') as \
         conf:
        conf.write("checks = {{'pre-commit': {0}}}\n".format(repr(checks)))
    run_steps("""
    When the user installs glerbl
    And answers affirmatively the install prompt
    """)
    scc.proc.join()
    assert_equal(scc.proc.exitcode, 0)
    # These have become useless
    del scc.proc
    del scc.stdin
    del scc.stderr
    del scc.stdout

@Given("^([^ ]*?) exists$")
def x_exists(x):
    with open(os.path.join(scc.repo, x), 'w'):
        pass

@Given("^a non-ascii filename is staged$")
def non_ascii_exists():
    with open(os.path.join(scc.repo, u"ālaya"), 'w'):
        pass
    git(scc.repo, "git", "add", u"ālaya")

@Given("^a file with trailing whitespace is staged$")
def file_with_trailing_whitespace_staged():
    with open(os.path.join(scc.repo, u"foo"), 'w') as foo:
        foo.write("a = 'blah'  ")
    git(scc.repo, "git", "add", u"foo")

@Given("^a python file with a trailing semicolon is staged$")
def python_file_with_trailing_semicolon_staged():
    with open(os.path.join(scc.repo, u"foo.py"), 'w') as foo:
        foo.write("a = 'blah';")
    git(scc.repo, "git", "add", u"foo.py")

@Given("^a python file that violates PEP8 is staged$")
def python_file_that_violates_pep8_staged():
    with open(os.path.join(scc.repo, u"foo.py"), 'w') as foo:
        foo.write("a='blah'")
    git(scc.repo, "git", "add", u"foo.py")


@Given("^hooks.allownonascii is true$")
def hooks_allownonascii_true():
    git(scc.repo, "git", "config", "hooks.allownonascii", "true")

@Given(r"^environment variable (\w+) is set$")
def environment_variable_x_is_set(x):
    os.environ[x]="1"


@Given(r"^a staged deleted file which would normally be checked and "
       r"has no errors$")
def staged_deleted_file():
    my_path = os.path.join(scc.repo, u"staged_deleted.py")
    assert_false(os.path.exists(my_path), my_path + " must not exist")
    with open(my_path, 'w'):
        pass
    git(scc.repo, "git", "add", os.path.relpath(my_path, scc.repo))
    git(scc.repo, "git", "commit", "-q", "-m", "blah")
    git(scc.repo, "git", "rm", "-q",  os.path.relpath(my_path, scc.repo))


@Given(r"^an unstaged deleted file which would normally be checked and "
       r"has no errors$")
def unstaged_deleted_file():
    my_path = os.path.join(scc.repo, u"unstaged_deleted.py")
    assert_false(os.path.exists(my_path), my_path + " must not exist")
    with open(my_path, 'w'):
        pass
    git(scc.repo, "git", "add", os.path.relpath(my_path, scc.repo))
    git(scc.repo, "git", "commit", "-q", "-m", "blah")
    os.unlink(my_path)


@When("^the user installs glerbl$")
def user_installs_glerbl():
    with chdir(scc.repo):
        (proc, stdin, stdout, stderr) = start_glerbl(["glerbl", "install"])
        scc.proc = proc
        scc.stdin = stdin
        scc.stderr = stderr
        scc.stdout = stdout

@When("^answers affirmatively the install prompt$")
def user_answers_affirmatively():
    scc.stdin.write("yes\n")
    scc.stdin.flush()

@When("^the user commits$")
def the_user_commits():
    # We need to have something to commit
    insurance = os.path.join(scc.repo, "insurance")
    assert_false(os.path.exists(insurance), insurance + " must not exist")
    with open(insurance, 'w'):
        pass
    git(scc.repo, "git", "add", os.path.relpath(insurance, scc.repo))
    proc = subprocess.Popen(["git", "commit", "-m", "foo"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, cwd=scc.repo)
    (scc.git_stdout, scc.git_stderr) = proc.communicate()
    scc.git_returncode = proc.returncode # pylint: disable=E1101

@Then("^glerbl prompts the user$")
def glerbl_prompts_the_user():
    scc.stdin.write("N\n")
    scc.stdin.flush()
    done = False
    while not done:
        try:
            assert_equal(
                scc.stdout.read().strip(),
                "This will overwrite your current hooks. Proceed [yes/No]?")
            done = True
        except IOError:
            time.sleep(0.5)

@Then('^glerbl fails with "(.*?)"$')
def glerbl_fails_with(value):
    scc.proc.join()
    assert_equal(scc.stderr.read().strip(),
                 value.strip().decode('string_escape'))
    assert_equal(scc.proc.exitcode, 1)

@Then("^glerbl installs the hooks$")
def glerbl_installs_the_hooks():
    scc.proc.join()
    commit_hook_path = os.path.join(scc.repo, ".git/hooks/pre-commit")
    assert_true(os.path.exists(commit_hook_path))
    commit_hook = open(commit_hook_path, 'r')
    commit_hook.readline() # skip first line
    assert_equal(commit_hook.readline().strip(),
                "# GENRATED BY GLERBL. DO NOT MODIFY.")
    assert_equal(scc.proc.exitcode, 0)
    commit_hook.close()

@Then('^the commit fails with "(.*?)"$')
def commit_fails_with(value):
    assert_equal(scc.git_returncode, 1)
    assert_equal(scc.git_stderr.decode('utf-8'),
                 value.strip().decode('string_escape').decode('utf-8'))

@Then('^the commit fails with trailing "(.*?)"$')
def commit_fails_with_trailing(value):
    assert_equal(scc.git_returncode, 1)
    assert_true(scc.git_stderr.decode('utf-8').endswith(
        value.strip().decode('string_escape').decode('utf-8')))


@Then('^the commit is successful$')
def commit_successful():
    assert_equal(scc.git_returncode, 0)
