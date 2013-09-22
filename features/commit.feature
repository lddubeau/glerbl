Feature: glerbl runs pre-commit hooks

# Failures are tested in other feature files.

Scenario: no error, commit successful
Given a git repository in which all pre-commit hooks are to be run
And a staged file
When the user commits
Then the commit is successful
