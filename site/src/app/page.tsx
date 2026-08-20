import Link from "next/link";
import { ProductCard } from "@/components/product-card";
import { formatPrice, products, shipping } from "@/lib/catalog";
import { bikes, faq, metrics, steps, watches } from "@/lib/content";
import { site } from "@/lib/site";

const cheapest = products.reduce(
  (min, product) => (product.priceCents < min.priceCents ? product : min),
  products[0],
);

export default function Home() {
  return (
    <div className="mx-auto max-w-6xl px-6">
      <section className="grid gap-10 py-20 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="space-y-6">
          <p className="text-xs font-medium tracking-[0.18em] uppercase text-muted">
            Plug and play — rien à installer sur la montre
          </p>
          <h1 className="text-4xl font-semibold tracking-tight sm:text-5xl">
            {site.baseline}
          </h1>
          <p className="max-w-xl text-lg text-muted">{site.description}</p>
          <div className="flex flex-wrap items-center gap-4">
            <Link
              href="/boutique"
              className="rounded-full bg-foreground px-6 py-3 text-sm font-medium text-background transition-opacity hover:opacity-85"
            >
              Commander à partir de {formatPrice(cheapest.priceCents)}
            </Link>
            <Link
              href="/compatibilite"
              className="border-line rounded-full border px-6 py-3 text-sm font-medium transition-colors hover:bg-surface"
            >
              Mon vélo est-il compatible ?
            </Link>
          </div>
          <p className="text-sm text-muted">
            Livraison depuis le Canada, offerte dès{" "}
            {formatPrice(shipping.freeAboveCents)}.
          </p>
        </div>
        <div className="border-line rounded-2xl border bg-surface p-8">
          <p className="font-mono text-sm leading-7">
            Vélo de spinning
            <br />
            <span className="text-muted">└─ Bluetooth ─┐</span>
            <br />
            Boîtier {site.name}
            <br />
            <span className="text-muted">└─ Bluetooth ou ANT+ ─┐</span>
            <br />
            Montre Garmin
          </p>
          <p className="mt-6 text-sm text-muted">
            La montre voit un capteur de puissance standard. L&apos;activité est
            enregistrée comme n&apos;importe quelle sortie, puis synchronisée dans
            Garmin Connect et Strava.
          </p>
        </div>
      </section>

      <section className="border-line border-t py-16">
        <h2 className="text-2xl font-semibold tracking-tight">Comment ça marche</h2>
        <ol className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((step, index) => (
            <li key={step.title} className="space-y-2">
              <p className="text-sm text-muted">0{index + 1}</p>
              <h3 className="font-medium">{step.title}</h3>
              <p className="text-sm text-muted">{step.body}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="border-line border-t py-16">
        <h2 className="text-2xl font-semibold tracking-tight">
          Ce que la montre enregistre
        </h2>
        <dl className="mt-8 grid gap-6 sm:grid-cols-2">
          {metrics.map((metric) => (
            <div key={metric.name} className="border-line rounded-xl border p-5">
              <dt className="font-medium">{metric.name}</dt>
              <dd className="mt-1 text-sm text-muted">{metric.detail}</dd>
            </div>
          ))}
        </dl>
        <p className="mt-6 text-sm text-muted">
          Séries Garmin concernées : {watches.join(", ")}, et tout modèle acceptant un
          capteur de puissance externe.
        </p>
      </section>

      <section className="border-line border-t py-16">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h2 className="text-2xl font-semibold tracking-tight">Vélos pris en charge</h2>
          <Link href="/compatibilite" className="text-sm underline underline-offset-4">
            Tous les détails
          </Link>
        </div>
        <ul className="mt-8 grid gap-6 sm:grid-cols-3">
          {bikes.map((bike) => (
            <li key={bike.name} className="border-line rounded-xl border p-5">
              <p className="font-medium">{bike.name}</p>
              <p
                className={`mt-1 text-sm ${bike.available ? "text-accent" : "text-muted"}`}
              >
                {bike.status}
              </p>
              <p className="mt-2 text-sm text-muted">{bike.note}</p>
            </li>
          ))}
        </ul>
      </section>

      <section id="produits" className="border-line border-t py-16">
        <h2 className="text-2xl font-semibold tracking-tight">Choisir son boîtier</h2>
        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard key={product.handle} product={product} />
          ))}
        </div>
      </section>

      <section className="border-line border-t py-16">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <h2 className="text-2xl font-semibold tracking-tight">Questions fréquentes</h2>
          <Link href="/faq" className="text-sm underline underline-offset-4">
            Toutes les questions
          </Link>
        </div>
        <div className="mt-8 space-y-4">
          {faq.slice(0, 4).map((item) => (
            <details key={item.question} className="border-line rounded-xl border p-5">
              <summary className="cursor-pointer font-medium">{item.question}</summary>
              <p className="mt-3 text-sm text-muted">{item.answer}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
}
