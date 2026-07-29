# /release

Bump the patch version, commit, push, and trigger the CI release pipeline.

## Steps

1. **Ensure working tree is clean**
   - Run `git status` — if there are uncommitted changes, run `/push` first and stop.

2. **Rebase onto main**
   ```bash
   git fetch origin main && git rebase origin/main
   ```

3. **Run /unittest**
   - All tests must pass before releasing.

4. **Bump the patch version**
   ```bash
   bumpversion patch
   ```
   This updates `pyproject.toml` and `.bumpversion.cfg` and creates a git tag (e.g. `v1.0.1032`).

5. **Commit and push with the tag**
   ```bash
   git push origin main --tags
   ```

6. **Create a GitHub Release from the tag**
   ```bash
   version=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
   gh release create "v${version}" --repo redhat-performance/benchmark-runner \
     --title "v${version}" \
     --generate-notes
   ```
   This creates the release at https://github.com/redhat-performance/benchmark-runner/releases.

7. **Trigger the Build Runner workflow**
   ```bash
   gh workflow run Build_runner.yml
   ```
   Then show the run URL:
   ```bash
   gh run list --workflow=Build_runner.yml --limit=1
   ```

## Notes

- Never release if unit tests fail.
- The CI pipeline (Build_runner.yml) handles PyPI upload, Quay image push, and auto-bumps the version after a successful release.
- After pushing, CI may take several minutes — use `gh run watch` to follow progress.
- Do not bump the version manually in `pyproject.toml`; always use `bumpversion patch`.
- The GitHub Release is created at https://github.com/redhat-performance/benchmark-runner/releases with auto-generated notes from merged PRs since the last release, including "What's Changed" (all merged PRs) and "New Contributors" (first-time contributors). Both sections are produced automatically by `--generate-notes`.
