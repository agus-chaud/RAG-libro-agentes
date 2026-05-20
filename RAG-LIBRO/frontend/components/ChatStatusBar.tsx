"use client";

import { CHAT_STATUS_LABELS, type ChatStatus } from "@/lib/chat";

const STATUS_STYLES: Record<
  ChatStatus,
  { dot: string; pill: string; ring: string }
> = {
  idle: {
    dot: "bg-zinc-400",
    pill: "bg-zinc-100 text-zinc-700 border-zinc-200",
    ring: "",
  },
  streaming: {
    dot: "bg-sky-500 animate-pulse",
    pill: "bg-sky-50 text-sky-800 border-sky-200",
    ring: "ring-2 ring-sky-200 ring-offset-1",
  },
  done: {
    dot: "bg-emerald-500",
    pill: "bg-emerald-50 text-emerald-800 border-emerald-200",
    ring: "",
  },
  error: {
    dot: "bg-red-500",
    pill: "bg-red-50 text-red-800 border-red-200",
    ring: "",
  },
};

type ChatStatusBarProps = {
  status: ChatStatus;
  errorMessage?: string | null;
};

export function ChatStatusBar({ status, errorMessage }: ChatStatusBarProps) {
  const styles = STATUS_STYLES[status];

  return (
    <div
      className="flex flex-wrap items-center gap-2"
      role="status"
      aria-live="polite"
      aria-label={`Estado del chat: ${CHAT_STATUS_LABELS[status]}`}
    >
      <span
        className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium transition-colors duration-300 ${styles.pill} ${styles.ring}`}
      >
        <span
          className={`h-2 w-2 shrink-0 rounded-full transition-colors duration-300 ${styles.dot}`}
          aria-hidden
        />
        {CHAT_STATUS_LABELS[status]}
      </span>
      {status === "error" && errorMessage ? (
        <span className="text-xs text-red-600">{errorMessage}</span>
      ) : null}
      {status === "streaming" ? (
        <span className="text-xs text-sky-600">Entrada bloqueada</span>
      ) : null}
    </div>
  );
}
