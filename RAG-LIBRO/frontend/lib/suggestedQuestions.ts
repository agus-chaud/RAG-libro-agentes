/**
 * Preguntas sugeridas en la UI (one-click). Fuente de verdad del texto.
 * Mapeo a EVAL.md: Q01, Q07, Q08, Q05, Q06 — ver § UI — preguntas sugeridas.
 */
export const SUGGESTED_QUESTIONS = [
  "What is an AI agent according to this book?",
  "How does LangGraph support agent workflows?",
  "Compare reactive vs deliberative agents. When to choose each?",
  "How does the book store embeddings with FAISS?",
  "What is MCP (Model Context Protocol) and what problem does it solve?",
] as const;

export type SuggestedQuestion = (typeof SUGGESTED_QUESTIONS)[number];

const suggestedSet = new Set<string>(SUGGESTED_QUESTIONS);

/** True si el texto coincide con una pregunta sugerida (clic en botón). */
export function isSuggestedQuestion(text: string): text is SuggestedQuestion {
  return suggestedSet.has(text.trim());
}

/** Sugerencias que el usuario aún no envió (match exacto con mensajes user). */
export function getRemainingSuggestedQuestions(
  userContents: string[],
): SuggestedQuestion[] {
  const asked = new Set(userContents.map((c) => c.trim()));
  return SUGGESTED_QUESTIONS.filter((q) => !asked.has(q));
}
