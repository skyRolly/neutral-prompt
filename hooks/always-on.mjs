// SessionStart hook: injects the full neutral-prompt ruleset when the user has
// opted in by creating $CLAUDE_CONFIG_DIR/.neutral-prompt-always (default ~/.claude).
// Never blocks session start: any failure exits 0.
//
// Runs under Node so it works on macOS, Linux, and Windows. The hook declaration
// in hooks.json launches this module from the plugin-root environment variable
// rather than relying on platform-specific shell expansion for the script path.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

try {
  const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
  const flagPath = path.join(claudeDir, ".neutral-prompt-always");

  // Only fire when the user has opted in.
  if (!fs.existsSync(flagPath)) process.exit(0);

  // Resolve SKILL.md relative to this script's own location, not a trusted env var.
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const skillPath = path.join(scriptDir, "..", "skills", "neutral-prompt", "SKILL.md");
  if (!fs.existsSync(skillPath)) process.exit(0);
  // The rules name references/*.md relative to the skill folder; say where it is.
  const skillDir = path.dirname(skillPath);

  // Strip a leading YAML frontmatter block (--- ... --- at the very top of file).
  // An unterminated fence is not frontmatter, so the whole file is kept.
  const body = fs
    .readFileSync(skillPath, "utf8")
    .replace(/^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)/, "")
    .replace(/(?:\r?\n)+$/, "");

  process.stdout.write(
    "NEUTRAL PROMPT MODE ACTIVE (always-on). The rules below apply to every prompt " +
      'you write, review, or rewrite this session. "stop neutral mode" turns them off ' +
      `for this session; delete ${flagPath} to turn always-on off for good. The ` +
      `references/ paths below are relative to ${skillDir}.\n\n${body}\n`,
  );
} catch {
  // Never block session start.
  process.exit(0);
}
