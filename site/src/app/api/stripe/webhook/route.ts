import { NextResponse } from "next/server";
import type Stripe from "stripe";
import { getStripe } from "@/lib/stripe";

/**
 * Réception des événements Stripe. La signature est vérifiée avec le corps brut
 * de la requête ; tant qu'aucun outil de gestion des commandes n'est branché,
 * les commandes payées sont relayées à `ORDER_WEBHOOK_URL` si la variable est
 * définie, sinon journalisées côté serveur.
 */
export async function POST(request: Request) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  const signature = request.headers.get("stripe-signature");
  if (!secret || !signature) {
    return NextResponse.json({ error: "Webhook non configuré." }, { status: 400 });
  }

  const payload = await request.text();
  let event: Stripe.Event;
  try {
    event = getStripe().webhooks.constructEvent(payload, signature, secret);
  } catch (error) {
    console.error("[stripe] signature refusée", error);
    return NextResponse.json({ error: "Signature invalide." }, { status: 400 });
  }

  if (event.type === "checkout.session.completed") {
    const session = event.data.object;
    const order = {
      sessionId: session.id,
      email: session.customer_details?.email ?? null,
      name: session.customer_details?.name ?? null,
      phone: session.customer_details?.phone ?? null,
      amountTotal: session.amount_total,
      currency: session.currency,
      articles: session.metadata?.articles ?? null,
      shipping: session.collected_information?.shipping_details ?? null,
    };

    const orderWebhook = process.env.ORDER_WEBHOOK_URL;
    if (orderWebhook) {
      try {
        await fetch(orderWebhook, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(order),
        });
      } catch (error) {
        console.error("[stripe] relais de commande impossible", error);
      }
    } else {
      console.info("[stripe] commande payée", order);
    }
  }

  return NextResponse.json({ received: true });
}
