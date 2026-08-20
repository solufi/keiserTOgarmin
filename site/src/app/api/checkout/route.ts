import { NextResponse } from "next/server";
import type Stripe from "stripe";
import {
  currency,
  findProduct,
  shipping,
  shippingCents,
  type Product,
} from "@/lib/catalog";
import { site } from "@/lib/site";
import { baseUrl, getStripe } from "@/lib/stripe";

type RequestedItem = { product: Product; quantity: number };

function parseItems(body: unknown): RequestedItem[] | null {
  if (typeof body !== "object" || body === null) return null;
  const rawItems = (body as Record<string, unknown>).items;
  if (!Array.isArray(rawItems) || rawItems.length === 0) return null;

  const items: RequestedItem[] = [];
  for (const raw of rawItems) {
    if (typeof raw !== "object" || raw === null) return null;
    const record = raw as Record<string, unknown>;
    const handle = typeof record.handle === "string" ? record.handle : "";
    const quantity = typeof record.quantity === "number" ? record.quantity : 1;
    const product = findProduct(handle);
    if (!product) return null;
    if (!Number.isInteger(quantity) || quantity < 1 || quantity > product.maxQuantity) {
      return null;
    }
    if (items.some((item) => item.product.handle === handle)) return null;
    items.push({ product, quantity });
  }
  return items;
}

function lineItems(items: RequestedItem[]): Stripe.Checkout.SessionCreateParams.LineItem[] {
  return items.map(({ product, quantity }) => ({
    quantity,
    price_data: {
      currency,
      unit_amount: product.priceCents,
      product_data: {
        name: product.title,
        description: product.tagline,
        metadata: { handle: product.handle, sku: product.sku },
      },
    },
  }));
}

function shippingOptions(
  subtotalCents: number,
): Stripe.Checkout.SessionCreateParams.ShippingOption[] {
  const amount = shippingCents(subtotalCents);
  return [
    {
      shipping_rate_data: {
        type: "fixed_amount",
        display_name: amount === 0 ? `${shipping.label} offerte` : shipping.label,
        fixed_amount: { amount, currency },
        delivery_estimate: {
          minimum: { unit: "business_day", value: shipping.deliveryDaysMin },
          maximum: { unit: "business_day", value: shipping.deliveryDaysMax },
        },
      },
    },
  ];
}

/**
 * Crée une session Stripe Checkout à partir du catalogue local. Les prix ne
 * viennent jamais du client : seuls le `handle` et la quantité sont acceptés.
 */
export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Requête invalide." }, { status: 400 });
  }

  const items = parseItems(body);
  if (!items) {
    return NextResponse.json(
      { error: "Article ou quantité invalide." },
      { status: 422 },
    );
  }

  let stripe;
  try {
    stripe = getStripe();
  } catch {
    return NextResponse.json(
      {
        error:
          "Le paiement n'est pas encore activé sur ce site. Écrivez-nous et nous prendrons la commande par courriel.",
      },
      { status: 503 },
    );
  }

  const origin = baseUrl(request);
  const subtotalCents = items.reduce(
    (total, { product, quantity }) => total + product.priceCents * quantity,
    0,
  );

  try {
    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      locale: "fr-CA",
      line_items: lineItems(items),
      shipping_address_collection: { allowed_countries: [...shipping.countries] },
      shipping_options: shippingOptions(subtotalCents),
      phone_number_collection: { enabled: true },
      allow_promotion_codes: true,
      automatic_tax: { enabled: process.env.STRIPE_AUTOMATIC_TAX === "true" },
      success_url: `${origin}/paiement/succes?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/boutique?paiement=annule`,
      metadata: {
        source: site.name,
        articles: items
          .map(({ product, quantity }) => `${product.sku}x${quantity}`)
          .join(","),
      },
    });

    if (!session.url) {
      throw new Error("Session Stripe sans URL de redirection");
    }
    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error("[checkout] création de session impossible", error);
    return NextResponse.json(
      { error: "Le paiement n'a pas pu démarrer. Réessayez dans un instant." },
      { status: 502 },
    );
  }
}
