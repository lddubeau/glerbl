Feature: python_no_trailing_semicolon reports errors

Scenario: commit fails when there is a trailing semicolon in a python file
  Given a git repository in which python_no_trailing_semicolon is to be run
  And a python file with a trailing semicolon is staged
  When the user commits
  Then the commit fails with "foo.py contains trailing semicolons; or was so mangled that pylint failed.\n.git/hooks/pre-commit: glerbl.check.python_no_trailing_semicolon failed.\n"
