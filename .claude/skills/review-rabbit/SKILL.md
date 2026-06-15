# /review-rabbit

Review CodeRabbit critical issues on a PR and report only the real problems.

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

3. **Analyze each critical issue**
   - Read the relevant source file and line for each finding
   - Determine if the issue is a real bug or a false positive
   - Skip issues where CodeRabbit couldn't verify (e.g., registry checks from sandbox)

4. **Report findings**
   - List only the real critical issues with file path, line number, and what needs to be fixed
   - If no real critical issues exist, report that the PR is clean

## Notes

- Focus only on critical issues — skip informational and style comments
- Always verify against the actual code before reporting
- Prefix any PR comment replies with [Claude Code]
