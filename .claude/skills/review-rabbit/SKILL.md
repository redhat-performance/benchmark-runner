# /review-rabbit

Review CodeRabbit critical issues and human reviewer comments on a PR. Report only the real problems.

## Usage

Pass the PR number as an argument: `/review-rabbit 1240`

If no argument is provided, use the current branch's open PR.

## Steps

1. **Find the PR**
   - If a PR number is provided, use it
   - Otherwise, find the open PR for the current branch:
     ```bash
     gh pr view --json number --jq '.number'
     ```

2. **Fetch CodeRabbit critical comments**
   ```bash
   gh api repos/redhat-performance/benchmark-runner/pulls/{PR_NUMBER}/comments \
     --jq '.[] | select(.user.login == "coderabbitai[bot]") | select(.body | test("Critical|critical|🔴")) | {path: .path, line: .line, body: .body[0:800]}'
   ```

3. **Fetch human reviewer comments (arpsharm and others)**
   ```bash
   gh api repos/redhat-performance/benchmark-runner/pulls/{PR_NUMBER}/comments \
     --jq '.[] | select(.user.login != "coderabbitai[bot]") | {id: .id, user: .user.login, path: .path, line: .line, body: .body[0:800]}'
   ```

4. **Analyze each issue**
   - Read the relevant source file and line for each finding
   - For CodeRabbit: determine if the issue is a real bug or a false positive; skip issues where CodeRabbit couldn't verify (e.g., registry checks from sandbox)
   - For human reviewers: treat every comment as a real concern that needs to be addressed

5. **Reply on the PR for fixed issues**
   - For every issue (CodeRabbit or human reviewer) that has already been fixed in the current branch, reply to the comment on the PR confirming the fix
   - Fetch comment IDs with:
     ```bash
     gh api repos/redhat-performance/benchmark-runner/pulls/{PR_NUMBER}/comments \
       --jq '.[] | select(.user.login == "coderabbitai[bot]") | select(.body | test("Critical|critical|🔴")) | {id: .id, path: .path, body: .body[0:200]}'
     ```
   - Reply to each fixed issue's comment:
     ```bash
     gh api repos/redhat-performance/benchmark-runner/pulls/{PR_NUMBER}/comments/{COMMENT_ID}/replies \
       -X POST \
       -f body='[Claude Code] Already fixed in commit {SHORT_SHA}. {Brief description of the fix}.'
     ```

6. **Report findings**
   - List real critical issues (CodeRabbit) and human reviewer comments with file path, line number, and what needs to be fixed
   - If no real issues exist, report that the PR is clean

## Notes

- Focus only on critical issues — skip informational and style comments
- Always verify against the actual code before reporting
- Prefix any PR comment replies with [Claude Code]
- Always reply to every CodeRabbit critical comment that has been fixed — do not skip duplicates
