import { spawnSync } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../..");
const pythonPath = resolve(root, "src");

function messageText(message: unknown): string {
  if (!message || typeof message !== "object") return "";
  const value = message as Record<string, unknown>;
  const content = value.content;
  if (typeof content === "string") return content;
  if (Array.isArray(content)) {
    return content
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && typeof (item as Record<string, unknown>).text === "string") {
          return String((item as Record<string, unknown>).text);
        }
        return "";
      })
      .filter(Boolean)
      .join("\n");
  }
  return "";
}

export default function meroPrecision(pi: ExtensionAPI) {
  let latestPrompt = "";
  let latestAssistant = "";
  let toolSummaries: string[] = [];

  pi.on("input", async (event) => {
    if (event.source === "extension") return { action: "continue" };
    latestPrompt = event.text;
    latestAssistant = "";
    toolSummaries = [];
    return { action: "continue" };
  });

  pi.on("turn_end", async (event) => {
    latestAssistant = messageText(event.message);
    toolSummaries.push(JSON.stringify(event.toolResults ?? []));
  });

  pi.on("agent_settled", async (_event, ctx) => {
    if (!latestPrompt) return;

    const payload = {
      conversation_id: ctx.sessionManager.getSessionId(),
      prompt: latestPrompt,
      last_assistant_message: latestAssistant,
      transcript_text: toolSummaries.join("\n"),
      fully_idle: ctx.isIdle(),
    };

    const result = spawnSync("python3", ["-m", "mero_precision.cli", "--host", "pi"], {
      cwd: root,
      env: { ...process.env, PYTHONPATH: pythonPath },
      input: JSON.stringify(payload),
      encoding: "utf8",
      timeout: 8_000,
    });

    if (result.error || result.status !== 0) return;

    try {
      const parsed = JSON.parse(result.stdout) as {
        enforce?: boolean;
        reason?: string;
        decision?: Record<string, unknown>;
      };

      pi.appendEntry("mero-precision-decision", parsed.decision ?? {});

      if (parsed.enforce && parsed.reason) {
        pi.sendMessage(
          {
            customType: "mero-precision",
            content: parsed.reason,
            display: false,
          },
          {
            triggerTurn: true,
            deliverAs: "followUp",
          },
        );
      }
    } catch {
      // Fail open. A malformed gate response must not trap the agent.
    }
  });
}
