"use client";

import { MessageSquare, Plus, Trash2 } from "lucide-react";

import { useAppStore } from "@/lib/store";

function preview(text: string) {
  return text.length > 72 ? `${text.slice(0, 72)}...` : text;
}

export function Sidebar() {
  const {
    sessions,
    currentSessionId,
    selectSession,
    createNewSession,
    removeSession,
    messages
  } = useAppStore();

  return (
    <aside className="panel flex h-full flex-col rounded-[30px] p-4">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.28em] text-[var(--color-ink-soft)]">
            Sessions
          </p>
          <h2 className="text-lg font-semibold tracking-[-0.04em]">会话与原始消息</h2>
        </div>
        <button
          className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[rgba(15,139,141,0.12)] text-ocean"
          onClick={() => void createNewSession()}
          type="button"
        >
          <Plus size={18} />
        </button>
      </div>

      <div className="space-y-2 overflow-y-auto pr-1">
        {sessions.map((session) => (
          <div
            className={`rounded-3xl border px-4 py-3 transition ${
              session.id === currentSessionId
                ? "border-transparent bg-[rgba(15,139,141,0.16)]"
                : "border-[var(--color-line)] bg-white/45"
            }`}
            key={session.id}
          >
            <button
              className="w-full text-left"
              onClick={() => void selectSession(session.id)}
              type="button"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{session.title}</p>
                  <p className="mt-1 text-xs text-[var(--color-ink-soft)]">
                    {session.message_count} 条消息
                  </p>
                </div>
                <MessageSquare className="mt-1 text-[var(--color-ink-soft)]" size={16} />
              </div>
            </button>
            <button
              className="mt-3 flex items-center gap-2 text-xs text-[var(--color-ember)]"
              onClick={() => void removeSession(session.id)}
              type="button"
            >
              <Trash2 size={14} />
              删除
            </button>
          </div>
        ))}
      </div>

      <div className="mt-4 flex min-h-0 flex-1 flex-col rounded-[24px] border border-[var(--color-line)] bg-white/40 p-3">
        <p className="text-xs uppercase tracking-[0.28em] text-[var(--color-ink-soft)]">
          Raw Messages
        </p>
        <div className="mt-3 space-y-3 overflow-y-auto pr-1">
          {messages.map((message) => (
            <div
              className="rounded-2xl border border-[var(--color-line)] bg-white/60 px-3 py-2"
              key={message.id}
            >
              <div className="mb-1 flex items-center justify-between text-xs uppercase tracking-[0.2em] text-[var(--color-ink-soft)]">
                <span>{message.role}</span>
                <span>{message.toolCalls.length} tools</span>
              </div>
              <p className="text-sm text-[var(--color-ink-soft)]">{preview(message.content)}</p>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
