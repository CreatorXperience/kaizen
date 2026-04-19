![Uploading ChatGPT Image Apr 19, 2026, 10_47_47 PM.png…]()

# Kaizen (TLDR-ON-STEROIDS 💪)

Kaizen is a terminal tool that turns Unix `man` pages into a compact, TLDR-like command guide.

It fetches a command's manual page, parses it into a structured object, extracts useful options and examples, and prints a short command-oriented summary that is easier to learn from than a full manual page.

Kaizen is designed to work with both GNU-style and BSD-style man pages.

## What It Does

- Fetches a local `man` page for a command
- Normalizes terminal-formatted man output
- Parses the page into structured data such as:
  - command name
  - aliases
  - summary
  - synopsis entries
  - options
  - examples
  - raw sections
- Builds a TLDR-like result from parsed examples and options
- Caches results for faster repeated lookups

## How It Works

The high-level flow is:

1. `man <command>` is fetched locally.
2. The raw output is cleaned and normalized.
3. The parser splits the page into sections like `NAME`, `SYNOPSIS`, `DESCRIPTION`, `OPTIONS`, and `EXAMPLES`.
4. Kaizen builds a structured `ManPage` object.
5. Parsed examples are preferred for output; parsed options are used as fallback command suggestions.
6. The final result is rendered as a Rich terminal view and cached on disk.

## Requirements

- Python 3
- A Unix-like environment with the `man` command available

## Running Kaizen

From the repository root:

```bash
./kaizen.sh --help
```

If you prefer:

```bash
python3 kaizen.sh --help
```

## CLI Usage

Top-level help:

```bash
./kaizen.sh --help
```

Available commands:

- `search`: fetch and summarize a command
- `list`: list cached queries
- `clear`: clear the cache

### Search

Search for a command and print a TLDR-like summary:

```bash
./kaizen.sh search ls
./kaizen.sh search grep
./kaizen.sh search tar
```

Options:

- `--update`, `-u`: bypass cache and rebuild the result
- `--offline`, `-o`: only use cached results
- `--limit`, `-l`: limit the number of commands shown

Examples:

```bash
./kaizen.sh search grep --limit 5
./kaizen.sh search tar --update
./kaizen.sh search ls --offline
```

### List Cached Queries

```bash
./kaizen.sh list
```

### Clear Cache

```bash
./kaizen.sh clear
```

## Example Output

For a command like `grep`, Kaizen aims to show:

- a short command summary
- example commands from the `EXAMPLES` section when available
- useful option-based commands when example sections are missing

Typical output looks like:

```text
grep
file pattern searcher

Find all occurrences of the pattern `patricia' in a file:
grep 'patricia' myfile

Same as above but looking only for complete words:
grep -w 'patricia' myfile
```

This makes it easier to:

- support different man page styles
- render alternative output formats later
- add filters, export, or API support in the future

## Current Scope

Kaizen currently works best for commands that:

- have a local `man` page installed
- expose recognizable `NAME`, `SYNOPSIS`, `DESCRIPTION`, `OPTIONS`, or `EXAMPLES` sections
- include real example commands or clear option definitions

## Future Ideas

- better GNU/Linux fixture coverage in tests
- export output as JSON
- rank examples by usefulness
- generate task-based command suggestions
- package Kaizen for installation as a normal shell command
