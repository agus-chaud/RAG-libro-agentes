"use client";

import { SourceBadges } from "@/components/SourceBadges";
import type { ChatMessage } from "@/lib/chat";

type MessageListProps = {
  messages: ChatMessage[];
  streamingPreview?: string | null;
  streamingPages?: number[] | null;
};

export function MessageList({
  messages,
  streamingPreview,
  streamingPages,
}: MessageListProps) {
  const isEmpty = messages.length === 0 && !streamingPreview;

  return (
    <div
      className="flex-1 overflow-y-auto px-4 py-6"
      aria-label="Historial de mensajes"
    >
      {isEmpty ? (
        <p className="mx-auto max-w-md text-center text-sm text-zinc-500">
          Preguntá sobre el libro. Las respuestas llegan en streaming desde el
          backend con las páginas citadas.
        </p>
      ) : (
        <ul className="mx-auto flex max-w-2xl flex-col gap-4">
          {messages.map((msg) => (
            <li
              key={msg.id}
              className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-zinc-900 text-white"
                    : "border border-zinc-200 bg-white text-zinc-800 shadow-sm"
                }`}
              >
                <span className="sr-only">
                  {msg.role === "user" ? "Tú" : "Asistente"}:{" "}
                </span>
                {msg.content}
              </div>
              {msg.role === "assistant" && msg.pages && msg.pages.length > 0 ? (
                <div className="max-w-[85%] px-1">
                  <SourceBadges pages={msg.pages} />
                </div>
              ) : null}
            </li>
          ))}
          {streamingPreview ? (
            <li className="flex flex-col items-start">
              <div className="max-w-[85%] rounded-2xl border border-sky-200 bg-sky-50 px-4 py-2.5 text-sm leading-relaxed text-zinc-800">
                <span className="sr-only">Asistente: </span>
                {streamingPreview}
                <span
                  className="ml-0.5 inline-block h-4 w-0.5 animate-pulse bg-sky-600 align-middle"
                  aria-hidden
                />
              </div>
              {streamingPages && streamingPages.length > 0 ? (
                <div className="max-w-[85%] px-1">
                  <SourceBadges pages={streamingPages} />
                </div>
              ) : null}
            </li>
          ) : null}
        </ul>
      )}
    </div>
  );
}
