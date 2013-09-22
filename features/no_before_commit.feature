Feature: no_before_commit reports errors

Scenario: BEFORE_COMMIT exists, commit fails
  Given a git repository in which no_before_commit is to be run
  And a staged file
  And BEFORE_COMMIT exists
  When the user commits
  Then the commit fails with "BEFORE_COMMIT exists.\n.git/hooks/pre-commit: glerbl.check.no_before_commit failed.\n"

Scenario: BEFORE-COMMIT exists, commit fails
  Given a git repository in which no_before_commit is to be run
  And a staged file
  And BEFORE-COMMIT exists
  When the user commits
  Then the commit fails with "BEFORE-COMMIT exists.\n.git/hooks/pre-commit: glerbl.check.no_before_commit failed.\n"

Scenario: When the environment variable IGNORE_BEFORE_COMMIT is set,
    no_before_commit ignores the presence of the offending files.
  Given a git repository in which no_before_commit is to be run
  And a staged file
  And BEFORE_COMMIT exists
  And BEFORE-COMMIT exists
  And environment variable IGNORE_BEFORE_COMMIT is set
  When the user commits
  Then the commit is successful
