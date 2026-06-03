name: paperpilot
description: "A specialized local agent skill to parse and deeply analyze academic PDFs. It extracts research problems, methods, datasets, innovations, and limitations using LLMs."
tools:

exec

How to use this skill

When the user asks to analyze an academic paper (e.g., "Analyze the paper at /path/to/paper.pdf"), use the exec tool to run the provided CLI script.

Command Syntax

To get a Markdown report (default):

python app/cli.py /absolute/path/to/the/paper.pdf


To get structured JSON output (useful for piping into other tools):

python app/cli.py /absolute/path/to/the/paper.pdf --format json


Important Notes for Agent

Always ensure the provided path is absolute and correct.

The environment variable DEEPSEEK_API_KEY must be set in the sandbox before execution.

If the script outputs an error to stderr, inform the user about the failure reason.