"use client";

import { type FormEvent, useRef, useEffect } from "react";
import { canSendMessage, type ChatStatus } from "@/lib/chat";

type ChatInputProps = {
  status: ChatStatus;
  onSubmit: (text: string) => void;
};

export function ChatInput({ status, onSubmit }: ChatInputProps) {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const disabled = !canSendMessage(status);

  useEffect(() => {
    if (!disabled) {
      inputRef.current?.focus();
    }
  }, [disabled]);

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const text = inputRef.current?.value.trim() ?? "";
    if (!text || disabled) return;
    onSubmit(text);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="border-t border-zinc-200 bg-white px-4 py-4"
    >
      <div className="mx-auto flex max-w-2xl gap-2">
        <label htmlFor="chat-input" className="sr-only">
          Mensaje
        </label>
        <textarea
          id="chat-input"
          ref={inputRef}
          rows={2}
          placeholder={
            disabled
              ? "Esperá a que termine la respuesta…"
              : "Escribí tu pregunta sobre el libro…"
          }
          disabled={disabled}
          className="min-h-[44px] flex-1 resize-none rounded-xl border border-zinc-300 bg-zinc-50 px-3 py-2 text-sm text-zinc-900 transition-colors placeholder:text-zinc-400 focus:border-zinc-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-zinc-200 disabled:cursor-not-allowed disabled:opacity-60"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              e.currentTarget.form?.requestSubmit();
            }
          }}
        />
        <button
          type="submit"
          disabled={disabled}
          className="shrink-0 self-end rounded-xl bg-zinc-900 px-4 py-2 text-sm font-medium text-white transition-opacity hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-40"
        >
          Enviar
        </button>
      </div>
    </form>
  );
}
