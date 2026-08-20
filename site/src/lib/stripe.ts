import Stripe from "stripe";

let client: Stripe | null = null;

/**
 * Client Stripe créé à la première utilisation : le site doit pouvoir être
 * construit et affiché sans clé, seul le paiement exige la configuration.
 */
export function getStripe(): Stripe {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey) {
    throw new Error("STRIPE_SECRET_KEY manquante");
  }
  if (!client) {
    client = new Stripe(secretKey);
  }
  return client;
}

export function isStripeConfigured(): boolean {
  return Boolean(process.env.STRIPE_SECRET_KEY);
}

/** URL publique utilisée pour les retours de paiement. */
export function baseUrl(request: Request): string {
  const configured = process.env.NEXT_PUBLIC_SITE_URL;
  if (configured) return configured.replace(/\/$/, "");
  return new URL(request.url).origin;
}
