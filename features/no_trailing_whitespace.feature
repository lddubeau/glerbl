Feature: no_trailing_whitespace reports errors

Scenario: commit fails when there is trailing whitespace
  Given a git repository in which no_trailing_whitespace is to be run
  And a file with trailing whitespace is staged
  When the user commits
  Then the commit fails with trailing ".git/hooks/pre-commit: glerbl.check.no_trailing_whitespace failed.\n"
