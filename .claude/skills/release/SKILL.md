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

4. **Bump the patch version, commit, and tag**
   ```bash
   set -euo pipefail
   branch=$(git rev-parse --abbrev-ref HEAD)
   if [ "$branch" != "main" ]; then
     echo "release must run on main, currently on $branch" >&2
     exit 1
   fi
   next=$(python3 -c "import tomllib; v=tomllib.load(open('pyproject.toml','rb'))['project']['version'].split('.'); print(f'{v[0]}.{v[1]}.{int(v[2]) + 1}')")
   if git rev-parse -q --verify "refs/tags/v${next}" >/dev/null; then
     echo "tag v${next} already exists" >&2
     exit 1
   fi
   bump-my-version bump patch --commit --tag \
     --tag-name "v{new_version}" \
     -m "bump version to v{new_version}"
   version=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
   git push origin main "v${version}"
   ```
   `bump-my-version` rewrites `pyproject.toml`, commits it, and creates `v<version>` on that commit in one step. Install it once with `pip install bump-my-version`.

5. **Create a GitHub Release from the tag**
   ```bash
   version=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
   gh release create "v${version}" --repo redhat-performance/benchmark-runner \
     --title "v${version}" \
     --generate-notes
   ```
   This creates the release at https://github.com/redhat-performance/benchmark-runner/releases.

6. **Trigger the Build Runner workflow**
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
- Do not bump the version manually in `pyproject.toml`; always use `bump-my-version bump patch`.
- The GitHub Release is created at https://github.com/redhat-performance/benchmark-runner/releases with auto-generated notes from merged PRs since the last release, including "What's Changed" (all merged PRs) and "New Contributors" (first-time contributors). Both sections are produced automatically by `--generate-notes`.
