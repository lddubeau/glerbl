Feature: no_non_ascii_filenames reports errors

Scenario: non-ascii filename exists, commit fails
  Given a git repository in which no_non_ascii_filenames is to be run
  And a non-ascii filename is staged
  When the user commits
  Then the commit fails with "ālaya is a non-ascii filename.\n.git/hooks/pre-commit: glerbl.check.no_non_ascii_filenames failed.\n"

Scenario: non-ascii filename exists, hooks.allownonascii is true, commit successful
  Given a git repository in which no_non_ascii_filenames is to be run
  And hooks.allownonascii is true
  And a non-ascii filename is staged
  When the user commits
  Then the commit is successful
