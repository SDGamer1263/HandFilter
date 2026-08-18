You are working in my existing project.

I want you to deploy/publish this project to GitHub.

IMPORTANT:
- Do NOT delete, overwrite, or reset existing project files unnecessarily.
- Do NOT expose, commit, or upload secrets such as API keys, tokens, passwords, `.env` files, private credentials, or certificates.
- Inspect the project before making changes.
- Do NOT assume the GitHub repository name, account, or visibility if it is not already configured.

Follow this process:

1. Inspect the project
   - Read `README.md` if present.
   - Inspect the directory structure.
   - Check whether Git is already initialized.
   - Check the current Git status and branches.
   - Check whether a GitHub remote already exists.
   - Identify build artifacts, caches, dependencies, secrets, and other files that should not be committed.

2. Prepare the repository
   - Create or update `.gitignore` appropriately for this project's language/framework.
   - Make sure `.env`, API keys, credentials, `node_modules`, build caches, virtual environments, IDE files, and other sensitive/unnecessary files are excluded where appropriate.
   - Do NOT modify application logic just for the GitHub deployment.
   - If an existing `.gitignore` is present, improve it rather than blindly replacing it.

3. Validate the project
   - Run the project's appropriate lint/typecheck/test/build commands if they can be determined safely.
   - Fix only deployment-blocking issues that are clearly caused by the repository configuration.
   - Do not make unrelated code changes.
   - Report any pre-existing failures instead of hiding them.

4. Configure Git
   - If Git is not initialized, initialize it.
   - Check the current branch.
   - Create an appropriate initial commit if this is a new repository.
   - If commits already exist, preserve them.
   - Do not rewrite Git history unless absolutely necessary and explicitly confirmed.

5. Configure GitHub
   - Check whether `gh` (GitHub CLI) is installed and authenticated.
   - If already authenticated, use it where appropriate.
   - If a GitHub remote already exists, use the existing repository rather than creating a duplicate.
   - If no repository exists, ask me for the GitHub repository name and whether it should be public or private before creating it.
   - Do NOT ask me for or print my GitHub password or personal access token.

6. Push the project
   - Add the correct GitHub remote.
   - Push the appropriate branch.
   - Verify that the push completed successfully.
   - Confirm the final GitHub repository URL.

7. Final report
   Give me a concise summary containing:
   - GitHub repository URL
   - Branch pushed
   - Commit created/pushed
   - Whether the project was successfully pushed
   - Any files intentionally excluded
   - Any remaining warnings or issues

If something is missing or requires my authentication/permission, stop at that exact point and tell me what I need to do. Do not invent credentials, repository names, URLs, or configuration.

Start by inspecting the project. Do not make changes until you understand its current Git/GitHub state.