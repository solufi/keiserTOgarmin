import type { Metadata } from "next";
import Link from "next/link";
import { getStripe, isStripeConfigured } from "@/lib/stripe";

export const metadata: Metadata = {
  title: "Commande confirmée",
  robots: { index: false },
};

type OrderSummary = {
  email: string | null;
  total: string | null;
  articles: { description: string; quantity: number | null }[];
};

async function loadOrder(sessionId: string): Promise<OrderSummary | null> {
  if (!isStripeConfigured()) return null;
  try {
    const session = await getStripe().checkout.sessions.retrieve(sessionId, {
      expand: ["line_items"],
    });
    if (session.payment_status === "unpaid") return null;
    return {
      email: session.customer_details?.email ?? null,
      total:
        session.amount_total !== null && session.currency
          ? new Intl.NumberFormat("fr-CA", {
              style: "currency",
              currency: session.currency.toUpperCase(),
            }).format(session.amount_total / 100)
          : null,
      articles: (session.line_items?.data ?? []).map((item) => ({
        description: item.description ?? "Article",
        quantity: item.quantity,
      })),
    };
  } catch (error) {
    console.error("[succes] session introuvable", error);
    return null;
  }
}

export default async function SuccesPage({
  searchParams,
}: {
  searchParams: Promise<{ session_id?: string }>;
}) {
  const { session_id: sessionId } = await searchParams;
  const order = sessionId ? await loadOrder(sessionId) : null;

  return (
    <div className="mx-auto max-w-2xl px-6 py-20">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        Merci, commande reçue
      </h1>
      <p className="mt-4 text-muted">
        Le paiement est confirmé. Un reçu Stripe part
        {order?.email ? ` vers ${order.email}` : " vers votre courriel"}, suivi du numéro
        de suivi dès l&apos;expédition.
      </p>

      {order && order.articles.length > 0 && (
        <div className="border-line mt-8 rounded-xl border p-5 text-sm">
          <ul className="space-y-2">
            {order.articles.map((article) => (
              <li key={article.description} className="flex justify-between gap-4">
                <span>{article.description}</span>
                <span className="text-muted">× {article.quantity ?? 1}</span>
              </li>
            ))}
          </ul>
          {order.total && (
            <p className="border-line mt-4 flex justify-between border-t pt-4 font-medium">
              <span>Total</span>
              <span>{order.total}</span>
            </p>
          )}
        </div>
      )}

      <h2 className="mt-12 text-xl font-semibold">La suite</h2>
      <ol className="mt-4 space-y-3 text-sm text-muted">
        <li>1. Nous assemblons et configurons le boîtier, puis nous l&apos;expédions.</li>
        <li>
          2. À la réception : vous le branchez, vous choisissez votre vélo depuis votre
          téléphone, vous appairez la montre une fois.
        </li>
        <li>
          3. En cas de doute, la page{" "}
          <Link href="/installation" className="underline underline-offset-4">
            Installation
          </Link>{" "}
          reprend chaque étape.
        </li>
      </ol>

      <Link
        href="/"
        className="mt-12 inline-block rounded-full bg-foreground px-6 py-3 text-sm font-medium text-background transition-opacity hover:opacity-85"
      >
        Retour à l&apos;accueil
      </Link>
    </div>
  );
}
