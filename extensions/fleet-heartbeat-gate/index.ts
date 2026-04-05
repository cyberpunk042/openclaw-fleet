// Fleet Heartbeat Gate Plugin
//
// Uses before_agent_start hook to read .brain-decision.json from agent workspace.
// If decision is "silent", overrides the prompt to return HEARTBEAT_OK immediately
// without expensive reasoning.
//
// NOTE: before_agent_start cannot cancel the run, only modify it.
// For true cancellation, OpenArms needs a before_heartbeat hook or
// before_dispatch must fire for heartbeat triggers.
// This is a temporary approach that minimizes cost by setting minimal prompt.

import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

interface BrainDecision {
  decision: "silent" | "wake" | "strategic";
  agent: string;
  timestamp: string;
  reasons: Array<{ trigger: string; details: string; urgency: string }>;
  model_override?: string;
  effort_override?: string;
}

const DECISION_FILENAME = ".brain-decision.json";
const STALE_THRESHOLD_MS = 5 * 60 * 1000; // 5 minutes

function readBrainDecision(workspaceDir: string): BrainDecision | null {
  const path = join(workspaceDir, DECISION_FILENAME);
  if (!existsSync(path)) return null;

  try {
    const raw = readFileSync(path, "utf-8");
    const data = JSON.parse(raw) as BrainDecision;

    if (data.timestamp) {
      const age = Date.now() - new Date(data.timestamp).getTime();
      if (age > STALE_THRESHOLD_MS) return null;
    }

    return data;
  } catch {
    return null;
  }
}

export default function register(api: any) {
  api.registerHook(
    "before_agent_start",
    async (event: any, ctx: any) => {
      // Only gate heartbeats
      if (ctx.trigger !== "heartbeat") {
        return {};
      }

      const workspaceDir = ctx.workspaceDir;
      if (!workspaceDir) {
        return {};
      }

      const decision = readBrainDecision(workspaceDir);
      if (!decision) {
        return {};
      }

      if (decision.decision === "silent") {
        // Override prompt to minimal — agent will respond HEARTBEAT_OK quickly
        // with minimal token usage. Not a true cancellation but reduces cost.
        return {
          systemPrompt: "Respond with exactly: HEARTBEAT_OK",
          prependContext: "",
        };
      }

      if (decision.decision === "strategic" && decision.model_override) {
        return {
          modelOverride: decision.model_override,
        };
      }

      return {};
    },
    { name: "fleet-heartbeat-gate" },
  );
}
