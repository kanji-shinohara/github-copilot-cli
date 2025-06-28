import os
import subprocess
from github_copilot_cli.lib.logger import logger


def clone_repository(repository: str, source_branch: str, new_branch: str, working_directory: str):
    if not (repository and source_branch and working_directory):
        logger.warning('Missing required fields for clone action.')
        return

    if os.path.exists(working_directory):
        import shutil
        logger.info(f"Removing existing directory: {working_directory}")
        shutil.rmtree(working_directory)

    os.makedirs(working_directory, exist_ok=True)
    repo_name = repository if "/" in repository else f"{repository}"
    clone_cmd = ["gh", "repo", "clone", repo_name, f"{working_directory}/{repo_name}", "--", "-b", source_branch]
    logger.info(f"Cloning {repo_name} (branch: {source_branch}) into {working_directory} using gh cli")

    try:
        subprocess.run(clone_cmd, check=True)
    except subprocess.CalledProcessError as e:
        if b"not found in upstream origin" in (e.stderr or b"") or "not found in upstream origin" in str(e):
            logger.error(f"Branch '{source_branch}' not found in repository '{repo_name}'. Error: {e}")
        else:
            logger.error(f"Failed to clone repository: {e}")
        raise


def checkout_branch(repository: str, working_directory: str, new_branch: str):
    if not (repository and working_directory and new_branch):
        logger.warning('Missing required fields for checkout_branch action.')
        return
    cwd = os.path.abspath(f"{working_directory}/{repository}")
    subprocess.run(["git", "checkout", "-b", new_branch], cwd=cwd, check=True)
    logger.info(f"Created and switched to new branch: {new_branch}")


def push_changes(repository: str, working_directory: str, commit_message: str = "Update files via github-copilot-automator"):
    if not (repository and working_directory):
        logger.warning('Missing required fields for push_changes action.')
        return

    if not os.path.exists(working_directory):
        logger.error(f"Working directory does not exist: {working_directory}")
        return

    cwd = os.path.abspath(f"{working_directory}/{repository}")
    subprocess.run(["git", "add", "-A"], cwd=cwd, check=True)
    subprocess.run(["git", "commit", "-m", commit_message], cwd=cwd, check=True)
    subprocess.run(["git", "push", "--set-upstream", "origin", "HEAD"], cwd=cwd, check=True)
