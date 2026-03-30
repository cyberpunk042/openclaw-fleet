"""Tests for fleet.core.fleet_mode — fleet control state."""

import pytest
from fleet.core.fleet_mode import (
    FleetControlState,
    read_fleet_control,
    should_dispatch,
    should_pull_from_plane,
    get_active_agents_for_phase,
)


class TestReadFleetControl:
    def test_empty_config(self):
        state = read_fleet_control({})
        assert state.work_mode == "full-autonomous"
        assert state.cycle_phase == "execution"
        assert state.backend_mode == "claude"

    def test_full_config(self):
        state = read_fleet_control({
            "fleet_config": {
                "work_mode": "local-work-only",
                "cycle_phase": "planning",
                "backend_mode": "hybrid",
                "updated_by": "human",
            }
        })
        assert state.work_mode == "local-work-only"
        assert state.cycle_phase == "planning"
        assert state.backend_mode == "hybrid"
        assert state.updated_by == "human"

    def test_partial_config(self):
        state = read_fleet_control({
            "fleet_config": {"work_mode": "work-paused"}
        })
        assert state.work_mode == "work-paused"
        assert state.cycle_phase == "execution"  # default


class TestShouldDispatch:
    def test_full_autonomous(self):
        assert should_dispatch(FleetControlState(work_mode="full-autonomous"))

    def test_paused(self):
        assert not should_dispatch(FleetControlState(work_mode="work-paused"))

    def test_finish_current(self):
        assert not should_dispatch(FleetControlState(work_mode="finish-current-work"))

    def test_local_work(self):
        assert should_dispatch(FleetControlState(work_mode="local-work-only"))


class TestShouldPullFromPlane:
    def test_full_autonomous(self):
        assert should_pull_from_plane(FleetControlState(work_mode="full-autonomous"))

    def test_pm_work(self):
        assert should_pull_from_plane(FleetControlState(work_mode="project-management-work"))

    def test_local_work_only(self):
        assert not should_pull_from_plane(FleetControlState(work_mode="local-work-only"))

    def test_paused(self):
        assert not should_pull_from_plane(FleetControlState(work_mode="work-paused"))


class TestActiveAgentsForPhase:
    def test_execution_all_agents(self):
        assert get_active_agents_for_phase(FleetControlState(cycle_phase="execution")) is None

    def test_planning_pm_architect(self):
        agents = get_active_agents_for_phase(FleetControlState(cycle_phase="planning"))
        assert "project-manager" in agents
        assert "architect" in agents

    def test_review_fleet_ops(self):
        agents = get_active_agents_for_phase(FleetControlState(cycle_phase="review"))
        assert agents == ["fleet-ops"]

    def test_crisis_ops_devsecops(self):
        agents = get_active_agents_for_phase(FleetControlState(cycle_phase="crisis-management"))
        assert "fleet-ops" in agents
        assert "devsecops-expert" in agents