type SourceBadgesProps = {
  pages: number[];
};

/** Chips de páginas fuente bajo mensajes del asistente (fase 3d). */
export function SourceBadges({ pages }: SourceBadgesProps) {
  if (pages.length === 0) return null;

  const unique = Array.from(new Set(pages)).sort((a, b) => a - b);

  return (
    <div
      className="mt-2 flex flex-wrap gap-1.5"
      aria-label={`Fuentes: páginas ${unique.join(", ")}`}
    >
      {unique.map((page) => (
        <span
          key={page}
          className="inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-xs font-medium text-amber-900"
        >
          p. {page}
        </span>
      ))}
    </div>
  );
}
