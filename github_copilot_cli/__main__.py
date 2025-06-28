

import argparse
import yaml
import os
import time

from github_copilot_cli.lib.logger import logger, set_logging_config
from github_copilot_cli.lib.git_actions import clone_repository, push_changes, checkout_branch
from github_copilot_cli.lib.exec_github_copilot_chat import exec_github_copilot_chat


def github_copilot_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, default=None)
    parser.add_argument("--working_directory", type=str, default=None, help="Working directory for Copilot chat")
    parser.add_argument("--chat_message", type=str, default=None)
    parser.add_argument("--spec_file", type=str, default=None, help="Path to the specification file")
    parser.add_argument("--wait_response_time", type=int, default=60)
    parser.add_argument("--log_level", type=str, default="INFO", choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"])
    parser.add_argument("--log_file", type=str, default=None, help="Path to the log file")
    parser.add_argument("--only_logs", action="store_true", help="If set, only logs will be printed without console output")
    args = parser.parse_args()

    set_logging_config(args.log_level, args.log_file, args.only_logs)

    # If --spec_file is not specified (user did not provide a spec file or it does not exist), run exec_github_copilot_chat directly
    if not args.spec_file or not os.path.exists(args.spec_file):
        if not args.file or not args.chat_message or not args.working_directory:
            logger.error("--file, --working_directory, and --chat_message must be specified when --spec_file is not provided.")
            return
        logger.info(f"Executing Copilot chat for file: {args.file}")
        exec_github_copilot_chat(args.chat_message, args.working_directory, args.file, args.wait_response_time)
        return

    with open(args.spec_file, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    logger.debug(f"Loaded specification: {spec}")

    # Get global settings from spec.yml
    global_config = spec.get('global', {})

    # Get spec actions from spec.yml
    actions = spec.get('spec', [])

    for action in actions:
        act = action.get('action')

        if act == 'chat':
            file_to_open = action.get('file')
            chat_message = global_config.get('chat_message', '') or action.get('chat_message', args.chat_message)
            wait_response_time = global_config.get('wait_response_time', 60) or action.get('wait_response_time', args.wait_response_time)
            working_directory = global_config.get('working_directory') or action.get('working_directory') or \
                next(
                    (
                        (a.get('working_directory') or global_config.get('working_directory'))
                        for a in actions
                        if a.get('action') == 'clone' and (a.get('repository') or global_config.get('repository')) == (action.get('repository') or global_config.get('repository'))
                    ),
                    None
                )  # noqa: E123

            if not file_to_open:
                logger.warning('No file specified for chat action.')
                continue

            # Convert to path under the cloned directory
            if working_directory:
                file_to_open_path = os.path.join(working_directory, file_to_open)
            else:
                file_to_open_path = file_to_open

            logger.info(f"Executing Copilot chat for file: {file_to_open_path}")
            exec_github_copilot_chat(chat_message, working_directory, file_to_open_path, wait_response_time)
            time.sleep(1)

        elif act == 'clone':
            repository = global_config.get('repository') or action.get('repository')
            source_branch = action.get('source_branch')
            working_directory = global_config.get('working_directory') or action.get('working_directory')

            logger.info(f"Cloning repository {repository}...")
            clone_repository(repository, source_branch, None, working_directory)

        elif act == 'checkout':
            working_directory = global_config.get('working_directory') or action.get('working_directory')
            new_branch = action.get('new_branch')
            logger.info(f"Checking out new branch {new_branch} in {working_directory} ...")
            checkout_branch(working_directory, new_branch)

        elif act == 'push':
            working_directory = global_config.get('working_directory') or action.get('working_directory')
            commit_message = action.get('commit_message', 'Update files via github-copilot-automator')

            logger.info(f"Pushing changes in {working_directory} ...")
            push_changes(working_directory, commit_message)

        else:
            logger.warning(f"Unknown action: {act}. Skipping this action.")


if __name__ == "__main__":
    github_copilot_cli()
