# Privacy policy

Sequence Circuit does not create accounts and does not require a login.

## What we receive

If you call a locally running compiler (CLI, stdio MCP, or the static browser workspace), YAML never leaves your machine.

If you point ChatGPT, Claude, or another client at a **self-hosted** streamable-HTTP MCP URL that you operate, that host receives the spec YAML for that one tool call in order to validate, evaluate, or draw it.

## What we store

We do not store spec YAML, sheets, IP addresses, or chat transcripts in this software. There is no database and no analytics pipeline in the compiler.

A host you operate may keep ordinary web-server access logs. That is your policy, not this repository's.

## Recipients

- **Self-hosted CLI / stdio MCP / Pyodide workspace:** none.
- **ChatGPT:** if you install a plugin that uses a remote MCP, OpenAI receives the tool call. On ChatGPT Free, Go, Plus, and Pro, OpenAI may use app content to train models when **Improve the model for everyone** is on. Review OpenAI's policy for your plan.
- **Claude:** if you add a custom or directory connector, Anthropic receives the tool call under Anthropic's terms.

## Retention

In this software: no retention. Request in, response out.

## Restricted data

Do not send payment-card data, health records, government identifiers, or credentials in YAML. The compiler does not need them.

## Contact

See [SUPPORT.md](SUPPORT.md). Replace `https://REPLACE_ON_DEPLOY/` with your public origin if you host a remote MCP.
