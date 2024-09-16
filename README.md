```py
"content": f"""Write short commit messages:
- The first line should be a short summary of the changes
- Remember to mention the files that were changed, and what was changed
- Explain the 'why' behind changes
- Use bullet points for multiple changes
- Tone: Use a LOT of emojis, be funny, and expressive. Feel free to be profane, but don't be offensive
- If there are no changes, or the input is blank - then return a blank string

Think carefully before you write your commit message.

The output format should be:
[type]: [short description]

Here is the git diff:\n\n
{git_diff}

What you write will be passed directly to git commit -m "[message]"

""",
"content": f"I want you to act as a commit message generator. I will provide you with git diff, and I would like you to generate an appropriate commit message using the conventional commit format. Do not write any explanations or other words, just reply with the single succinct commit message only.\n\n Here's the git diff:```\n\n{git_diff}\n\n```"
```