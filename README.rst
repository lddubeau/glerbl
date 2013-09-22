Glerbl is a tool to help manage git hooks and promote consistent
coding standards among contributors to a repository.

Let's say you maintain a github repository for which you want to ensure
the following coding standards:

* No trailing spaces.
* No non-ascii file names.
* All python code must conform to pep8.

You can hope that contributors will remember to run the necessary
checks before they send in pull requests or push code to the
repository.

Or you can use glerbl to formalize your requirements and provide all
collaborators with the means to detect problems and fix these problems
before they commit.

.. Everything above goes into setup.py's long_description.

Requirements
============

Glerbl currently requires a POSIX-compliant system to run. There's
nothing that would *inherently* prevent it from running on other
systems, though.

Using
=====

Readers should keep the following distinctions in mind while reading:

Git hook

 A hook as git understands it. Git supports multiple hooks but each
 hook is unique. That is, git supports multiple hook in the sense that
 there can be a ``pre-commit`` and a ``post-commit`` hook. These are
 two different hooks. However there can be one and only one
 ``pre-commit`` hook at at time, and one ``post-commit`` hook at a
 time, etc.

Glerbl check

  A glerbl check runs when a specific git hook runs, but there may be
  multiple glerbl checks per git hook.

.. warning:: Glerbl will **completely** take over any git hook you ask
             it to manage. So if you ask glerbl to install any glerbl
             pre-commit check, it will remove
             ``.git/hooks/pre-commit`` and install its own
             script. Glerbl is **not** designed to work well with any
             other hook management system. However, glerbl is designed
             to leave alone any git hook you don't ask it to manage.

Create a directory named ``.glerbl`` in the root of your git
repository and in it a file named ``repo_conf.py``. That file must
assign a dictionary to a top level variable named ``check``. Each key
of this dictionary must be a git hook type (``pre-commit`` and so
on). Each value must be a list of checks to perform. Checks are
modules under ``glerbl.check``. The list of checks in the
configuration file can be the name of the module which performs the
check, relative to ``glerbl.check``. To get a list of available checks
you can use::

    $ glerbl listchecks

A ``.glerbl/repo_conf.py`` file could look like::

    checks = {
        "pre-commit": ["no_before_commit", "no_non_ascii_filenames",
                       "no_trailing_whitespace", "python_no_trailing_semicolon",
                       "python_pep8"]
    }

Once your file is set, you can issue::

    $ glerbl install

at the top of your working tree. Glerbl will ask whether you want to
proceed with the installation. Type "yes" (the whole word) if you want
to proceed. Anything else will abort the installation. Glerbl will
report errors if there are a problems.

Configuration Files
===================

The file ``.glerbl/repo_conf.py`` has already been mentioned. This
file is meant to record the standards under which a repository
operates. Therefore, this file should be tracked by git and should
reflect the minimum standards everyone who contribute to the
repository must follow. But what if a contributor wants to add more
checks to fit his or her local needs? This contributor could edit
``repo_conf.py``, but then this file would keep showing up in git as
modified. Committing the changes would be risky because these local
changes should not propagate upstream. There could be a command line
option to point glerbl to a different configuration file but then the
contributor would have to remember to pass this option.

Glerbl solves this problem by looking for a file named
``.glerbl/local_conf.py``. If this file is present, then *this* file
is read as configuration *instead* of ``.glerbl/repo_conf.py`` The
file ``.glerbl/local_conf.py`` can safely be put in ``.gitignore``.

Design Notes
============

Glerbl is a collection of checks, written in Python. If you want to
use another language, convert glerbl to your language or choice, or
use another tool.

Those hooks that check the data about to be committed are run on
**what HEAD will look like once what is staged is committed**. So if
file X is staged but file Y is not, glerbl's hooks won't check
file Y. Also if you staged only some hunks of file X, then only those
hunks that are staged will get checked. Glerbl does this by
duplicating the working tree into a temporary location, extracting the
contents of the files from the staging area onto those files at this
location, and deleting those that are to be deleted in the
commit. I've seen quite a few hooks on the internet that would run
tools like pylint on the *working tree* itself. Imagine the following
scenario. You've added ``import foo`` to file X.  You've staged this
modification but you erroneously forgot to stage the *new file*
``foo.py``. If pylint is run against the working tree, you won't get
an error regarding this problem because your working tree is fine. If
pylint is run against what HEAD will look like instead of the working
tree, pylint will report being unable to import ``foo``.

FAQ
===

Q. I get why glerbl does not run checks against the working tree but
   when I stage files partially, the error reports I get are useless
   because the files I have access to in the working tree are
   different from those files that are staged.

A. ``git stash`` is your friend. Stash what you are not
   committing. This way your working tree is identical to what HEAD
   will look like once the commit goes through. Try to commit
   again. Fix the problems. Commit. Pop the stash.

   Another way to solve this problem is using tools that prevent the
   problems reported by glerbl's hooks form *happening* in the first
   place. For instance, Emacs can be configured to automatically strip
   trailing space. Or if the issues cannot be automatically fixed,
   then using tools that *show* problems *as they occur* can also help.

Q. I need to commit automatically generated code which violates some
   of the checks I've asked glerbl to perform. For instance, code
   generated by South.

A. Stage *only* the automatically generated code and use ``git commit
   --no-verify`` to temporarily bypass the pre-commit checks. (Glerbl
   might eventually acquire a way to disable checks more selectively
   than this.)

   Note that if glerbl checked the files in the working tree rather
   than against the post-commit HEAD you'd have to actually remove
   files from your working tree to get around this problem. Or you'd
   have to use ``--no-verify`` while committing files that *should* be
   checked, thereby risking letting errors slip through.

Q. What about someone who wants to cause trouble? They just won't run
   glerbl on their "contribution".

A. See the next question.

Q. Why not use server-side hooks to ensure my standards? That seems
   safer to me because there's no guarantee that a contributor will
   run glerbl at all.

A. Repository hosting services rarely allow you to set your own custom
   server-side hooks. A prime example is github.

   Supporting server-side hooks would also require glerbl to be more
   sophisticated than it is right now. Consider the case where you
   want to exclude file F form hook's H's checks because F is
   generated by a third-party tool. You'd have to have a way to **tell
   the server** that H is not to be run on F.

   There *is* a way to simulate server-side checks designed to prevent
   letting inadequate code enter a repository. For instance, a pull
   request has been issued on github. On your computer, check out the
   branch onto which the code is to be pulled, pull onto it the code
   in the request. Run::

       GIT_DIR=`pwd`/.git .git/hooks/pre-commit

   Fix errors as needed. (This could mean telling the contributor that
   they did not use glerbl properly, etc.)

   Since github allows you to install hooks to get notification of
   events like pull requests, this could conceivably be automated.

All of glerbl's code and documentation is Copyright 2013
Louis-Dominique Dubeau.

..  LocalWords:  Glerbl github ascii glerbl py's pre repo py glerbl's
..  LocalWords:  listchecks filenames whitespace gitignore pwd
