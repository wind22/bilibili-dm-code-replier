.PHONY: test

test:
	python3 -c 'import pathlib; paths = ("skills/bilibili-dm-code-replier/scripts/code_ledger.py", "skills/bilibili-dm-code-replier/scripts/issue_log.py"); [compile(pathlib.Path(path).read_text(encoding="utf-8"), path, "exec") for path in paths]'
	tmpdir=$$(mktemp -d); \
	trap 'rm -rf "$$tmpdir"' EXIT; \
	python3 skills/bilibili-dm-code-replier/scripts/code_ledger.py stats \
		--codes examples/code.example.csv \
		--ledger "$$tmpdir/sent-ledger.csv"; \
	next_code=$$(python3 skills/bilibili-dm-code-replier/scripts/code_ledger.py next \
		--codes examples/code.example.csv \
		--ledger "$$tmpdir/sent-ledger.csv"); \
	test "$$next_code" = "GL-EXAMPLE-0001"; \
	python3 skills/bilibili-dm-code-replier/scripts/code_ledger.py mark-sent \
		--ledger "$$tmpdir/sent-ledger.csv" \
		--code "$$next_code" \
		--recipient "测试用户" \
		--source examples/code.example.csv; \
	python3 skills/bilibili-dm-code-replier/scripts/issue_log.py append \
		--log "$$tmpdir/issue-log.csv" \
		--recipient "测试用户" \
		--category "其他问题" \
		--message "测试消息" \
		--source-url "https://message.bilibili.com/"
