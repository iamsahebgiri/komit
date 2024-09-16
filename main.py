import os
import subprocess
import argparse
import logging
from typing import Dict, Any
from openai import OpenAI

from halo import Halo

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_URL", "http://localhost:8080/v1"),
)


def get_git_diff() -> str:
    return subprocess.check_output(["git", "diff", "HEAD"]).decode("utf-8")


def create_commit(message: str) -> None:
    subprocess.run(
        ["git", "commit", "-F", "-"], input=message.encode("utf-8"), check=True
    )


def main():
    parser = argparse.ArgumentParser(
        description="Automagically generate commit messages."
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Output the generated message, but don't create a commit.",
    )
    parser.add_argument(
        "-r",
        "--review",
        action="store_true",
        help="Edit the generated commit message before committing.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Don't ask for confirmation before committing.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    if not client.api_key:
        logging.error("Please set the OPENAI_API_KEY environment variable.")
        exit(1)

    if (
        not subprocess.check_output(["git", "rev-parse", "--is-inside-work-tree"])
        .decode("utf-8")
        .strip()
        == "true"
    ):
        logging.error("It looks like you are not in a git repository.")
        exit(1)

    git_diff = get_git_diff()
    if not git_diff:
        logging.error("There are no staged files to commit.")
        exit(1)

    if not args.dry_run:
        logging.info("Loading Data...")

    spinner = None
    if not args.dry_run and not args.verbose:
        spinner = Halo(text="Analyzing...", spinner="dots")
        spinner.start()

    try:
        response = client.chat.completions.create(
            model="llama-3.1",
            temperature=0.5,
            messages=[
                {
                    "role": "system",
                    "content": "You are an experienced programmer who writes great commit messages using commitzen guidelines.",
                },
                {
                    "role": "user",
                    "content": f"Here's the git diff:\n\n{git_diff}\n\nI want you to act as a commit message generator. I will provide you with information about the task and the prefix for the task code, and I would like you to generate an appropriate commit message using the conventional commit format. Do not write any explanations or other words, just reply with the commit message.",
                },
            ],
        )

        if spinner:
            spinner.stop()
            print("Finished Analyzing!")

        commit_msg = response.choices[0].message.content

        if args.dry_run:
            print(commit_msg)
        else:
            print(f"Proposed Commit:\n{'-' * 30}\n{commit_msg}\n{'-' * 30}")

            if not args.force:
                if input("Do you want to continue? (Y/n) ").lower() not in [
                    "y",
                    "yes",
                    "",
                ]:
                    logging.error("Commit aborted by user.")
                    exit(1)
                logging.info("Committing Message...")

            if args.review:
                subprocess.run(
                    ["git", "commit", "-e", "-F", "-"],
                    input=commit_msg.encode("utf-8"),
                    check=True,
                )
            else:
                create_commit(commit_msg)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)


if __name__ == "__main__":
    main()
