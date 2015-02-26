Feature: python_pep8 reports errors

Scenario: commit fails when there is python file violating PEP8
  Given a git repository in which python_pep8 is to be run
  And a python file that violates PEP8 is staged
  When the user commits
  Then the commit fails with "foo.py does not comply with pep8.\n.git/hooks/pre-commit: glerbl.check.python_pep8 failed.\n"

Scenario: commit fails when there is python file violating PEP8
  Given a git repository in which {"name": "python_pep8", "params": {"verbose": True}} is to be run
  And a python file that violates PEP8 is staged
  When the user commits
  Then the commit fails matching "./.*?/tree_from_staged/foo.py:1:2: E225 missing whitespace around operator\n./.*?/tree_from_staged/foo.py:1:9: W292 no newline at end of file\nfoo.py does not comply with pep8.\n.git/hooks/pre-commit: glerbl.check.python_pep8 failed.\n"
