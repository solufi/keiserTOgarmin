import type { Metadata } from "next";
import Link from "next/link";
import { bikes, metrics, watches } from "@/lib/content";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Compatibilité",
  description:
    "Vélos pris en charge, vélos en préparation, montres et appareils compatibles.",
};

export default function CompatibilitePage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Compatibilité</h1>
      <p className="mt-4 text-muted">
        Le boîtier traduit le signal d&apos;un vélo de salle vers les protocoles que les
        montres comprennent déjà. Chaque vélo demande son propre décodage : la liste
        ci-dessous s&apos;allonge par mises à jour, sans changer de matériel.
      </p>

      <h2 className="mt-12 text-xl font-semibold">Vélos</h2>
      <ul className="mt-6 space-y-4">
        {bikes.map((bike) => (
          <li key={bike.name} className="border-line rounded-xl border p-5">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="font-medium">{bike.name}</p>
              <p className={`text-sm ${bike.available ? "text-accent" : "text-muted"}`}>
                {bike.status}
              </p>
            </div>
            <p className="mt-2 text-sm text-muted">{bike.note}</p>
          </li>
        ))}
      </ul>

      <h2 className="mt-12 text-xl font-semibold">Montres et compteurs</h2>
      <p className="mt-4 text-muted">
        Toute montre ou tout compteur acceptant un capteur de puissance externe convient,
        notamment les séries {watches.join(", ")}. En Bluetooth, un seul appareil se
        connecte à la fois ; en ANT+, plusieurs appareils peuvent capter la même séance.
      </p>

      <h2 className="mt-12 text-xl font-semibold">Données transmises</h2>
      <dl className="mt-6 space-y-4">
        {metrics.map((metric) => (
          <div key={metric.name}>
            <dt className="font-medium">{metric.name}</dt>
            <dd className="text-sm text-muted">{metric.detail}</dd>
          </div>
        ))}
      </dl>

      <p className="mt-12 text-sm text-muted">
        Un doute sur votre modèle ?{" "}
        <a href={`mailto:${site.email}`} className="underline underline-offset-4">
          Écrivez-nous
        </a>{" "}
        avant de commander, ou consultez la{" "}
        <Link href="/faq" className="underline underline-offset-4">
          FAQ
        </Link>
        .
      </p>
    </div>
  );
}
