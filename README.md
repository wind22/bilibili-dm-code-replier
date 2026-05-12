# bilibili-dm-code-replier

Codex skill for processing unread Bilibili private messages, sending campaign redemption-code replies when screenshot evidence is present, requesting screenshots when needed, and logging non-code issues.

## Features

- Processes only unread private-message rows that visibly have a red dot, unread count, or equivalent unread marker.
- Detects code-related requests such as `三连`, `截图`, `兑换码`, `code`, `福利`, `21h`, and `领取`.
- Sends the configured screenshot-request reply when a code-related thread has no screenshot evidence.
- Allocates the next unused redemption code only when a user-provided screenshot/image is visible.
- Records sent codes in an append-only ledger after the browser UI shows the reply was sent.
- Logs opened unread non-code conversations by category: `产品体验问题`, `加速体验问题`, or `其他问题`.

## Repository Layout

```text
bilibili-dm-code-replier/
├── README.md
├── .gitignore
├── LICENSE
├── Makefile
├── skills/
│   └── bilibili-dm-code-replier/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── scripts/
│           ├── code_ledger.py
│           └── issue_log.py
└── examples/
    └── code.example.csv
```

## Install

Install from a local clone:

```bash
mkdir -p ~/.codex/skills
cp -R skills/bilibili-dm-code-replier ~/.codex/skills/
```

Or install a specific path from GitHub in Codex:

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo owner/bilibili-dm-code-replier \
  --path skills/bilibili-dm-code-replier
```

Replace `owner/bilibili-dm-code-replier` with the real GitHub repository.

## CSV Format

Preferred format:

```csv
code,note
GL-EXAMPLE-0001,example only
GL-EXAMPLE-0002,example only
```

Rules:

- Prefer a `code` column.
- For a one-column CSV, the first column is treated as codes. A `code` header is optional.
- For a multi-column CSV without a `code` column, pass `--code-column <name>`.
- Do not commit real redemption-code CSV files. This repo ignores common local code and log filenames.

## Ledger Output

`scripts/code_ledger.py` writes an append-only sent-code ledger with:

```text
code,recipient,sent_at,source,note
```

The skill defaults to a sibling file next to your codes CSV named `<codes-file>.sent-ledger.csv` when no ledger path is provided. A code is recorded only after the Bilibili UI visibly confirms the message was sent.

Common commands:

```bash
python3 skills/bilibili-dm-code-replier/scripts/code_ledger.py stats \
  --codes examples/code.example.csv \
  --ledger /tmp/bilibili.sent-ledger.csv

python3 skills/bilibili-dm-code-replier/scripts/code_ledger.py next \
  --codes examples/code.example.csv \
  --ledger /tmp/bilibili.sent-ledger.csv

python3 skills/bilibili-dm-code-replier/scripts/code_ledger.py mark-sent \
  --ledger /tmp/bilibili.sent-ledger.csv \
  --code GL-EXAMPLE-0001 \
  --recipient "Bilibili display name or id" \
  --source examples/code.example.csv
```

## Issue Log Output

`scripts/issue_log.py` writes an append-only non-code issue log with:

```text
recipient,category,message,recorded_at,source_url,note
```

The skill defaults to a sibling file next to your codes CSV named `<codes-file>.issue-log.csv` when no issue-log path is provided.

Append an issue:

```bash
python3 skills/bilibili-dm-code-replier/scripts/issue_log.py append \
  --log /tmp/bilibili.issue-log.csv \
  --recipient "Bilibili display name or id" \
  --category 产品体验问题 \
  --message "visible other-party message content" \
  --source-url "https://message.bilibili.com/..."
```

## Codex Usage Example

After installation, ask Codex:

```text
Use $bilibili-dm-code-replier to process https://message.bilibili.com/ with my codes CSV at /absolute/path/to/code.csv.
Use /absolute/path/to/code.sent-ledger.csv as the sent ledger and /absolute/path/to/code.issue-log.csv as the issue log.
```

Log in to Bilibili manually when Codex asks. The skill will then process only visible unread private-message rows.

## Test

Run the lightweight script smoke test:

```bash
make test
```

The test compiles both Python scripts and exercises `stats`, `next`, `mark-sent`, and `issue_log append` against `examples/code.example.csv` with temporary output files.
