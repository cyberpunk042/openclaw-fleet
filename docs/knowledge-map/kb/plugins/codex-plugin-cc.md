# codex-plugin-cc

**Type:** Claude Code Plugin
**Source:** github.com/openai/codex-plugin-cc (11K stars)
**Assigned to:** FLEET-OPS, DEVSEC (review), ARCH (design challenge)

## Purpose

Cross-provider bridge to OpenAI Codex. 6 commands: setup, review, adversarial-review, rescue, status, result. Review gate pattern (Stop hook blocks completion until Codex approves).

## Configuration

Requires ChatGPT subscription or OpenAI API key. CAN point at LocalAI via config.toml but quality with small models is poor. Known bugs: sandbox bwrap (#18), review gate state mismatch (#59).

## Relationships

challenge system (cross-model challenge type), codex_review.py (fleet module), fleet-ops 7-step review (additional layer), Stop hook (review gate pattern), multi-backend router (OpenAI as backend)
