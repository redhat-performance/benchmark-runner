# /push

Commit all changes, rebase onto main, squash to one commit, run all unit tests, and push.

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

3. **Squash to a single commit**
   Every PR must contain exactly one commit. If the branch has more than one
   commit relative to main:
   ```bash
   git log --oneline origin/main..HEAD      # inspect first
   git reset --soft origin/main
   git commit -F -                          # combined message via heredoc
   ```
   Do not use `git rebase -i` — it is unavailable in this environment.

4. **Run /unittest**

5. **Push**
   ```bash
   git push
   ```
   Use `--force-with-lease` if the branch was rebased or squashed.

## Notes

- If there are no uncommitted changes and nothing new to push, stop early
- Never push if any unit test fails
- Always squash to one commit before pushing; a multi-commit PR will be rejected
- If `git push` is rejected after rebase, use `git push --force-with-lease`
