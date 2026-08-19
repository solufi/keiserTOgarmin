import type { Metadata } from "next";
import { ProductCard } from "@/components/product-card";
import { formatPrice, products, shipping } from "@/lib/catalog";

export const metadata: Metadata = {
  title: "Boutique",
  description:
    "Boîtiers assemblés et préconfigurés, livrés prêts à brancher. Paiement sécurisé par Stripe.",
};

export default async function BoutiquePage({
  searchParams,
}: {
  searchParams: Promise<{ paiement?: string }>;
}) {
  const { paiement } = await searchParams;

  return (
    <div className="mx-auto max-w-6xl px-6 py-16">
      <header className="max-w-2xl space-y-4">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Boutique</h1>
        <p className="text-muted">
          Chaque boîtier est assemblé, préconfiguré et testé avant l&apos;expédition.
          Livraison suivie à {formatPrice(shipping.flatRateCents)}, offerte dès{" "}
          {formatPrice(shipping.freeAboveCents)}. Paiement par Stripe : carte, Apple Pay
          et Google Pay.
        </p>
      </header>

      {paiement === "annule" && (
        <p
          role="status"
          className="border-line mt-8 rounded-xl border bg-surface p-4 text-sm"
        >
          Paiement annulé : rien n&apos;a été débité. Votre commande peut être relancée
          quand vous le souhaitez.
        </p>
      )}

      <div className="mt-10 grid gap-6 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard key={product.handle} product={product} />
        ))}
      </div>

      <section className="mt-16 grid gap-8 sm:grid-cols-2">
        {products.map((product) => (
          <div key={product.handle} className="space-y-2">
            <h2 className="font-medium">{product.title}</h2>
            <p className="text-sm text-muted">{product.description}</p>
            <p className="text-xs text-muted">Référence {product.sku}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
