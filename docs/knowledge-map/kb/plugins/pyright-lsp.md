# pyright-lsp

**Type:** Claude Code Plugin
**Source:** Official Anthropic (claude-plugins-official)
**Assigned to:** ALL Python agents

## Purpose

Continuous Python type checking via pyright language server. Automatic diagnostics after every edit. Code navigation (go to def, find refs).

## Configuration

Needs pyright binary: npm i -g pyright

## Relationships

quality-lint skill (type checking is linting), PostToolUse hook (diagnostics after edits), feature-implement (catch errors during coding), anti-corruption (type system prevents wrong code)
