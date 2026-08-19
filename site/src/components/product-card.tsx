import { BuyButton } from "@/components/buy-button";
import { formatPrice, type Product } from "@/lib/catalog";

export function ProductCard({ product }: { product: Product }) {
  return (
    <article
      className={`border-line flex flex-col gap-5 rounded-2xl border p-6 ${
        product.featured ? "bg-surface" : ""
      }`}
    >
      <header className="space-y-2">
        {product.featured && (
          <p className="text-xs font-medium tracking-[0.18em] uppercase text-muted">
            Recommandé
          </p>
        )}
        <h3 className="text-xl font-semibold">{product.title}</h3>
        <p className="text-muted">{product.tagline}</p>
      </header>
      <p className="text-3xl font-semibold">{formatPrice(product.priceCents)}</p>
      <ul className="flex-1 space-y-2 text-sm">
        {product.includes.map((line) => (
          <li key={line} className="flex gap-2">
            <span aria-hidden className="text-muted">
              —
            </span>
            <span>{line}</span>
          </li>
        ))}
      </ul>
      <BuyButton product={product} variant={product.featured ? "primary" : "secondary"} />
    </article>
  );
}
