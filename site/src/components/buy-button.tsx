"use client";

import { useState } from "react";
import { formatPrice, type Product } from "@/lib/catalog";

type BuyButtonProps = {
  product: Product;
  variant?: "primary" | "secondary";
};

/** Achat direct d'un article : quantité puis redirection vers Stripe Checkout. */
export function BuyButton({ product, variant = "primary" }: BuyButtonProps) {
  const [quantity, setQuantity] = useState(1);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function checkout() {
    setPending(true);
    setError(null);
    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ items: [{ handle: product.handle, quantity }] }),
      });
      const data: { url?: string; error?: string } = await response.json();
      if (!response.ok || !data.url) {
        setError(data.error ?? "Le paiement n'a pas pu démarrer.");
        setPending(false);
        return;
      }
      window.location.assign(data.url);
    } catch {
      setError("Connexion impossible. Vérifiez votre réseau et réessayez.");
      setPending(false);
    }
  }

  const buttonClass =
    variant === "primary"
      ? "bg-foreground text-background hover:opacity-85"
      : "border border-line hover:bg-surface";

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <label htmlFor={`qty-${product.handle}`} className="text-sm text-muted">
          Quantité
        </label>
        <select
          id={`qty-${product.handle}`}
          value={quantity}
          onChange={(event) => setQuantity(Number(event.target.value))}
          className="border-line rounded-md border bg-background px-2 py-1 text-sm"
        >
          {Array.from({ length: product.maxQuantity }, (_, index) => index + 1).map(
            (value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ),
          )}
        </select>
      </div>
      <button
        type="button"
        onClick={checkout}
        disabled={pending}
        className={`w-full rounded-full px-5 py-3 text-sm font-medium transition-opacity disabled:opacity-60 ${buttonClass}`}
      >
        {pending
          ? "Redirection vers le paiement…"
          : `Acheter — ${formatPrice(product.priceCents * quantity)}`}
      </button>
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
