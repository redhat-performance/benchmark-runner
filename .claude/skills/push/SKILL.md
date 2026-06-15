# /push

Commit all changes, rebase onto main, run all unit tests, and push.

## Steps

1. **Commit all uncommitted changes**
   - Stage all modified, deleted, and untracked files
   - Create a commit with a descriptive message summarizing the changes
   - If there are no uncommitted changes, skip this step

2. **Rebase onto main**
   ```bash
   git fetch origin main && git rebase origin/main
   ```
   If there are conflicts, resolve them and continue the rebase before proceeding.

3. **Run all unit tests**
   ```bash
   PYTHONPATH=. python3 -m pytest -v tests/unittest/
   ```
   All 26 tests must pass. If any fail, fix them before pushing.

4. **Push**
   ```bash
   git push
   ```
   Use `--force-with-lease` if the branch was rebased.

## Notes

- Never push if any unit test fails
- Never skip the rebase step — always stay up to date with main before pushing
- If `git push` is rejected after rebase, use `git push --force-with-lease`
