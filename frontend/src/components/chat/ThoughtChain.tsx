"use client";

import { TerminalSquare } from "lucide-react";

import type { ToolCall } from "@/lib/api";

export function ThoughtChain({ toolCalls }: { toolCalls: ToolCall[] }) {
  if (!toolCalls.length) {
    return null;
  }

  return (
    <details className="mb-4 rounded-3xl border border-[rgba(212,106,74,0.18)] bg-[rgba(212,106,74,0.08)] p-4">
      <summary className="flex cursor-pointer list-none items-center gap-2 text-sm font-medium text-[var(--color-ember)]">
        <TerminalSquare size={16} />
        工具调用 {toolCalls.length} 次
      </summary>
      <div className="mt-3 space-y-3">
        {toolCalls.map((toolCall, index) => (
          <div className="rounded-2xl bg-white/70 p-3" key={`${toolCall.tool}-${index}`}>
            <div className="mb-2 text-sm font-medium">
              {toolCall.tool}
            </div>
            <div className="space-y-2 text-xs">
              <div className="rounded-2xl bg-[rgba(13,37,48,0.06)] p-3">
                <div className="mb-1 font-medium text-[var(--color-ink-soft)]">Input</div>
                <pre className="mono whitespace-pre-wrap">{toolCall.input}</pre>
              </div>
              <div className="rounded-2xl bg-[rgba(13,37,48,0.06)] p-3">
                <div className="mb-1 font-medium text-[var(--color-ink-soft)]">Output</div>
                <pre className="mono whitespace-pre-wrap">{toolCall.output}</pre>
              </div>
            </div>
          </div>
        ))}
      </div>
    </details>
  );
}
