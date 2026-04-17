# AUTO-GENERATED-STYLE forwarder to the second brain's evolve tool.
# Follows the same pattern as tools/gateway.py and tools/view.py.
# The second brain runs the real evolution engine (score, scaffold, promote).
# Note: brain's evolve.py currently operates on the brain's own wiki; cross-wiki
# evolution via forwarding may require brain-side support for --wiki-root on
# the evolve subcommand. File existence here satisfies Tier 3 structural; full
# cross-wiki evolution is a future integration step.
"""Wiki evolve forwarder to the second brain (devops-solutions-research-wiki)."""

import os
import subprocess
import sys

_SECOND_BRAIN = '/home/jfortin/devops-solutions-research-wiki'
_VENV_PYTHON = '/home/jfortin/devops-solutions-research-wiki/.venv/bin/python'

env = os.environ.copy()
env["WIKI_EVOLVE_CALLER_DIR"] = os.getcwd()
env["PYTHONPATH"] = _SECOND_BRAIN + os.pathsep + env.get("PYTHONPATH", "")

sys.exit(subprocess.call(
    [_VENV_PYTHON, "-m", "tools.evolve"] + sys.argv[1:],
    cwd=_SECOND_BRAIN,
    env=env,
))
