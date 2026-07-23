# Pre-Merge Request Checklist

Before opening a Merge Request (MR) or Pull Request (PR), ensure you have completed the following steps to maintain the codebase's health and quality:

### 1. Code Quality & Correctness
- [ ] **Run Relevant Tests:** Ensure all unit tests, integration tests, and end-to-end tests related to your code changes pass. Your goal is to verify that your solution is correct and does not introduce regressions.
- [ ] **No Syntax Errors:** Ensure there are no syntax errors or linter warnings introduced by your change.
- [ ] **No Debugging Artifacts:** Remove all unnecessary print statements, `console.log`s, and temporary test files/directories.

### 2. Frontend Verification (If Applicable)
- [ ] **Visual Verification:** If your changes modify the frontend (HTML, CSS, JS, JSX), you must write and execute a Playwright script to verify the visual changes.
- [ ] **Record Proof:** Generate screenshots and/or video recordings demonstrating the core user journey affected by your change.
- [ ] **Inspect Output:** Visually inspect the generated screenshots/videos to confirm the feature looks exactly as intended and styling is correct.

### 3. Code Review & Feedback
- [ ] **Self-Review:** Perform a self-review of your code to ensure readability, efficiency, and adherence to project conventions.
- [ ] **Request AI/Peer Review:** Submit your code for review to an automated code review tool or a peer.
- [ ] **Implement Feedback:** Address any blocking issues or constructive feedback received during the review before merging.

### 4. Dependencies & Infrastructure
- [ ] **Update Requirements:** If you added or removed dependencies, ensure `requirements.txt`, `package.json`, or equivalent package manager files are correctly updated.
- [ ] **Environment Consistency:** Ensure new environment variables are documented (e.g., in a `.env.example` file).

### 5. Documentation & Learnings
- [ ] **Record Learnings:** Document key patterns, successful solutions, or repository-specific procedures you discovered during this task.
- [ ] **Update Readme/Docs:** If your change fundamentally alters how the application runs or is configured, update the `README.md` accordingly.
