"""Tests for fleet budget CLI command."""

import json
import os

from fleet.cli.budget import list_modes, main, set_mode, show_current, show_report


def test_show_current_returns_zero(capsys):
    """show_current runs without error."""
    result = show_current()
    assert result == 0
    captured = capsys.readouterr()
    assert "Budget Mode" in captured.out


def test_list_modes_no_modes(capsys):
    """list_modes handles empty BUDGET_MODES (TBD)."""
    result = list_modes()
    assert result == 0


def test_set_mode_valid(tmp_path, capsys):
    """set_mode writes to fleet.yaml."""
    import yaml

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "fleet.yaml"
    config_file.write_text("orchestrator:\n  budget_mode: standard\n")

    result = set_mode("economic", fleet_dir=str(tmp_path))
    assert result == 0

    with open(config_file) as f:
        cfg = yaml.safe_load(f)
    assert cfg["orchestrator"]["budget_mode"] == "economic"


def test_set_mode_creates_section(tmp_path):
    """set_mode creates orchestrator section if missing."""
    import yaml

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "fleet.yaml"
    config_file.write_text("{}\n")

    result = set_mode("turbo", fleet_dir=str(tmp_path))
    assert result == 0

    with open(config_file) as f:
        cfg = yaml.safe_load(f)
    assert cfg["orchestrator"]["budget_mode"] == "turbo"


def test_show_report_no_records(capsys):
    """show_report handles missing records dir."""
    result = show_report(fleet_dir="/nonexistent")
    assert result == 0
    captured = capsys.readouterr()
    assert "No dispatch records" in captured.out


def test_show_report_with_records(tmp_path, capsys):
    """show_report aggregates dispatch records."""
    records_dir = tmp_path / "state" / "dispatch_records"
    records_dir.mkdir(parents=True)

    for i, (model, agent) in enumerate([
        ("sonnet", "worker"),
        ("opus", "architect"),
        ("sonnet", "worker"),
    ]):
        with open(records_dir / f"t{i}.json", "w") as f:
            json.dump({
                "model": model,
                "agent_name": agent,
                "backend": "claude-code",
            }, f)

    result = show_report(fleet_dir=str(tmp_path))
    assert result == 0
    captured = capsys.readouterr()
    assert "3 dispatches" in captured.out
    assert "sonnet" in captured.out
    assert "opus" in captured.out


# ─── CLI Entry Point ──────────────────────────────────────────────


def test_main_no_args(capsys):
    """main() with no args shows current."""
    result = main([])
    assert result == 0


def test_main_modes(capsys):
    """main(['modes']) lists modes."""
    result = main(["modes"])
    assert result == 0


def test_main_unknown_command(capsys):
    """main(['xyz']) returns error."""
    result = main(["xyz"])
    assert result == 1


def test_main_help(capsys):
    result = main(["help"])
    assert result == 0
