"use client";

/**
 * FleetControlBar — Three control dropdowns in the OCMC header.
 *
 * Always visible on every page. Three independent axes:
 * - Work Mode: where new work comes from
 * - Cycle Phase: what kind of work agents do
 * - Backend Mode: which AI backend
 *
 * Reads/writes board.fleet_config via PATCH API.
 */

import { useCallback, useEffect, useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/auth/clerk";

const WORK_MODES = [
  { value: "full-autonomous", label: "Full Autonomous" },
  { value: "project-management-work", label: "PM Work" },
  { value: "local-work-only", label: "Local Work Only" },
  { value: "finish-current-work", label: "Finish Current" },
  { value: "work-paused", label: "Work Paused" },
];

const CYCLE_PHASES = [
  { value: "execution", label: "Execution" },
  { value: "planning", label: "Planning" },
  { value: "analysis", label: "Analysis" },
  { value: "investigation", label: "Investigation" },
  { value: "review", label: "Review" },
  { value: "crisis-management", label: "Crisis" },
];

const BACKEND_MODES = [
  { value: "claude", label: "Claude" },
  { value: "localai", label: "LocalAI" },
  { value: "hybrid", label: "Hybrid" },
];

interface FleetControlBarProps {
  boardId?: string;
}

export function FleetControlBar({ boardId }: FleetControlBarProps) {
  const { isSignedIn } = useAuth();
  const [workMode, setWorkMode] = useState("full-autonomous");
  const [cyclePhase, setCyclePhase] = useState("execution");
  const [backendMode, setBackendMode] = useState("claude");
  const [loading, setLoading] = useState(false);

  // Fetch current fleet_config from board
  useEffect(() => {
    if (!isSignedIn || !boardId) return;

    const fetchConfig = async () => {
      try {
        const resp = await fetch(`/api/v1/boards/${boardId}`);
        if (resp.ok) {
          const board = await resp.json();
          const config = board.fleet_config || {};
          setWorkMode(config.work_mode || "full-autonomous");
          setCyclePhase(config.cycle_phase || "execution");
          setBackendMode(config.backend_mode || "claude");
        }
      } catch {
        // Silent fail — keep defaults
      }
    };

    fetchConfig();
  }, [isSignedIn, boardId]);

  // Update fleet_config on the board
  const updateConfig = useCallback(
    async (updates: Record<string, string>) => {
      if (!boardId || loading) return;
      setLoading(true);

      try {
        const currentConfig = {
          work_mode: workMode,
          cycle_phase: cyclePhase,
          backend_mode: backendMode,
          updated_at: new Date().toISOString(),
          updated_by: "human",
        };

        const newConfig = { ...currentConfig, ...updates };

        await fetch(`/api/v1/boards/${boardId}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fleet_config: newConfig }),
        });
      } catch {
        // Silent fail
      } finally {
        setLoading(false);
      }
    },
    [boardId, workMode, cyclePhase, backendMode, loading],
  );

  const handleWorkModeChange = (value: string) => {
    setWorkMode(value);
    updateConfig({ work_mode: value });
  };

  const handleCyclePhaseChange = (value: string) => {
    setCyclePhase(value);
    updateConfig({ cycle_phase: value });
  };

  const handleBackendModeChange = (value: string) => {
    setBackendMode(value);
    updateConfig({ backend_mode: value });
  };

  if (!boardId) return null;

  return (
    <div className="flex items-center gap-2">
      <Select value={workMode} onValueChange={handleWorkModeChange}>
        <SelectTrigger
          className="h-8 w-[150px] rounded-md border-slate-200 bg-white px-2 text-xs font-medium text-slate-700 shadow-none"
          disabled={loading}
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {WORK_MODES.map((mode) => (
            <SelectItem key={mode.value} value={mode.value}>
              {mode.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={cyclePhase} onValueChange={handleCyclePhaseChange}>
        <SelectTrigger
          className="h-8 w-[120px] rounded-md border-slate-200 bg-white px-2 text-xs font-medium text-slate-700 shadow-none"
          disabled={loading}
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {CYCLE_PHASES.map((phase) => (
            <SelectItem key={phase.value} value={phase.value}>
              {phase.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      <Select value={backendMode} onValueChange={handleBackendModeChange}>
        <SelectTrigger
          className="h-8 w-[100px] rounded-md border-slate-200 bg-white px-2 text-xs font-medium text-slate-700 shadow-none"
          disabled={loading}
        >
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {BACKEND_MODES.map((mode) => (
            <SelectItem key={mode.value} value={mode.value}>
              {mode.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}