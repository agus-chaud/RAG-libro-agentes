"use client";

import { getApiUrl } from "@/lib/api";

/** Verifica en runtime que NEXT_PUBLIC_API_URL llega al bundle del cliente. */
export function ApiUrlBadge() {
  const apiUrl = getApiUrl();

  return (
    <p className="text-sm text-zinc-600">
      API:{" "}
      <code className="rounded bg-zinc-100 px-2 py-0.5 font-mono text-zinc-800">
        {apiUrl}
      </code>
    </p>
  );
}
