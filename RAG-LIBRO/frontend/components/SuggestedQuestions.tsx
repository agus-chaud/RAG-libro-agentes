"use client";

import type { SuggestedQuestion } from "@/lib/suggestedQuestions";

type SuggestedQuestionsProps = {
  questions: readonly SuggestedQuestion[];
  /** Pantalla vacía: texto intro; con historial: etiqueta compacta. */
  compact?: boolean;
  disabled?: boolean;
  onSelect: (question: string) => void;
};

export function SuggestedQuestions({
  questions,
  compact = false,
  disabled = false,
  onSelect,
}: SuggestedQuestionsProps) {
  if (questions.length === 0) return null;

  return (
    <div
      className={`mx-auto flex w-full max-w-2xl flex-col gap-3 ${compact ? "mt-6 border-t border-zinc-200 pt-6" : ""}`}
    >
      {!compact ? (
        <p className="text-center text-sm text-zinc-500">
          Preguntá sobre el libro. Las respuestas llegan en streaming desde el
          backend con las páginas citadas.
        </p>
      ) : null}
      <p
        className={
          compact
            ? "text-xs font-medium uppercase tracking-wide text-zinc-400"
            : "text-center text-xs font-medium uppercase tracking-wide text-zinc-400"
        }
      >
        {compact ? "Más preguntas sugeridas" : "Probar con una pregunta sugerida"}
      </p>
      <ul className="flex flex-col gap-2" role="list">
        {questions.map((question) => (
          <li key={question}>
            <button
              type="button"
              disabled={disabled}
              onClick={() => onSelect(question)}
              className="w-full rounded-xl border border-zinc-200 bg-white px-4 py-3 text-left text-sm leading-snug text-zinc-800 shadow-sm transition-colors hover:border-zinc-300 hover:bg-zinc-50 focus:outline-none focus:ring-2 focus:ring-zinc-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {question}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
