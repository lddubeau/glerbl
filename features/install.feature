Feature: Glerbl can be installed

Scenario: Installing in a non-git directory
Given a non-git directory
When the user installs glerbl
Then glerbl fails with "glerbl: not in a git repo."

Scenario: Installing without a configuration
Given a git repository
When the user installs glerbl
Then glerbl fails with "glerbl: cannot load .glerbl/local_conf.py or .glerbl/repo_conf.py."

Scenario: Installing with a local_conf.py but no repo_conf.py
Given a git repository
And a local_conf.py file
When the user installs glerbl
Then glerbl fails with "glerbl: .glerbl/local_conf.py exists but not .glerbl/repo_conf.py."

Scenario: Installing with a configuration that does not have checks
Given a git repository
And a configuration that does not have the checks variable
When the user installs glerbl
Then glerbl fails with "glerbl: global ``checks`` variable missing from configuration."

Scenario: Installing with a configuration that refers to a non-existent check
Given a git repository
And a configuration that refers to a non-existent check
When the user installs glerbl
Then glerbl fails with "glerbl: cannot import the module for check name nonexistent."

Scenario: Installing with a configuration that does not apply a check to a hook for which it is designed to work.
Given a git repository
And a configuration that refers to a check for the wrong hook
When the user installs glerbl
Then glerbl fails with "glerbl: post-commit not among those hooks supported by glerbl.check.no_before_commit.\nglerbl: invalid configuration."

Scenario: Installing with a correct configuration prompts the user.
Given a git repository
And a correct configuration
When the user installs glerbl
Then glerbl prompts the user

Scenario: Installing installs hooks
Given a git repository
And a correct configuration
When the user installs glerbl
And answers affirmatively the install prompt
Then glerbl installs the hooks
