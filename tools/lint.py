# AUTO-GENERATED-STYLE forwarder to the second brain's lint tool.
# Follows the same pattern as tools/gateway.py and tools/view.py.
# The second brain runs the real lint engine; we target our wiki path.
"""Wiki lint forwarder to the second brain (devops-solutions-research-wiki)."""

import os
import subprocess
import sys
from pathlib import Path

_SECOND_BRAIN = '/home/jfortin/devops-solutions-research-wiki'
_VENV_PYTHON = '/home/jfortin/devops-solutions-research-wiki/.venv/bin/python'

_OUR_WIKI = str(Path(__file__).resolve().parent.parent / "wiki")
_OUR_SCHEMA = str(Path(__file__).resolve().parent.parent / "wiki" / "config" / "wiki-schema.yaml")

_user_args = sys.argv[1:]
_has_path = any(not a.startswith("-") for a in _user_args)
_has_config = "--config" in _user_args

_cmd = [_VENV_PYTHON, "-m", "tools.lint"]
if not _has_path:
    _cmd.append(_OUR_WIKI)
if not _has_config:
    _cmd += ["--config", _OUR_SCHEMA]
_cmd += _user_args

env = os.environ.copy()
env["PYTHONPATH"] = _SECOND_BRAIN + os.pathsep + env.get("PYTHONPATH", "")

sys.exit(subprocess.call(_cmd, cwd=_SECOND_BRAIN, env=env))
