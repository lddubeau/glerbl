Feature: glerbl runs pre-commit hooks

# Failures are tested in other feature files.

Scenario: no error, commit successful
  Given a git repository in which all pre-commit checks are to be run
  And a staged file
  When the user commits
  Then the commit is successful

Scenario: deleted file staged, commit successful
  Given a git repository in which all pre-commit checks are to be run
  And a staged deleted file which would normally be checked and has no errors
  When the user commits
  Then the commit is successful

Scenario: deleted file unstaged, commit successful
  Given a git repository in which all pre-commit checks are to be run
  And an unstaged deleted file which would normally be checked and has no errors
  When the user commits
  Then the commit is successful

Scenario: no checks to run, commit successful
  Given a git repository in which all pre-commit checks are to be run
  And a staged file
  When the user removes all checks
  And the user commits
  Then the commit is successful
