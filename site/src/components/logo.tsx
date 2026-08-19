/** Logotype purement typographique : aucun fichier image à maintenir. */
export function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-baseline gap-[0.15em] text-lg ${className}`}>
      <span className="font-semibold tracking-[0.18em] uppercase">Spin</span>
      <span className="font-light tracking-[0.18em] uppercase">Bridge</span>
    </span>
  );
}
