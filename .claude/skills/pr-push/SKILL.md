# /pr-push

Prepare and push the current branch: rebase onto main, run all unit tests, and push.

## Steps

1. **Rebase onto main**
   ```bash
   git fetch origin main && git rebase origin/main
   ```
   If there are conflicts, resolve them and continue the rebase before proceeding.

2. **Run all unit tests**
   ```bash
   PYTHONPATH=. python3 -m pytest -v tests/unittest/
   ```
   All 26 tests must pass. If any fail, fix them before pushing.

3. **Push**
   ```bash
   git push
   ```
   Use `--force-with-lease` if the branch was rebased.

## Notes

- Never push if any unit test fails
- Never skip the rebase step — always stay up to date with main before pushing
- If `git push` is rejected after rebase, use `git push --force-with-lease`
