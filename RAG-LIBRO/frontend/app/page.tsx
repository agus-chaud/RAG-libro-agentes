import { ApiUrlBadge } from "@/components/ApiUrlBadge";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 bg-zinc-50 px-6">
      <header className="text-center">
        <h1 className="text-2xl font-semibold tracking-tight text-zinc-900">
          RAG-LIBRO
        </h1>
        <p className="mt-2 max-w-md text-zinc-600">
          Chat sobre el libro &quot;30 Agents Every AI Engineer Must Build&quot;
          — Fase 3a scaffold (chat en fases siguientes).
        </p>
      </header>
      <ApiUrlBadge />
    </div>
  );
}
