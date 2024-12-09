# pre-commit - run once
pip install pre-commit

# generates .git/hooks/pre-commit
pre-commit install

# VPN On - run every time
# it generates /Users/{user}/.config/rh-gitleaks/auth.jwt
pre-commit run --all-files

# New venv/ New repository
Run the following commands to remove specific directories:
* rm -rf /Users/{user}/.cache/pre-commit/
* rm -rf /Users/{user}/.config/pre-commit
* rm -rf /Users/{user}/.config/rh-gitleaks
* Important: Reboot your laptop to ensure the changes take effect after deleting these files.
After reboot:
* pre-commit install
* run: pre-commit run --all-files
Got the following error:
```
Local rh-pre-commit......................................................Failed
- hook id: rh-pre-commit
- exit code: 1
```
* Run the following cmd and enter the token
* /Users/{user}/.cache/pre-commit/{cache_id}/venv/bin/python3 -m rh_gitleaks login
* Verify that rh-gitleaks is generated
/Users/{user}/.config/rh-gitleaks
