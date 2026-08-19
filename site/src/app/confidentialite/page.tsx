import type { Metadata } from "next";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Confidentialité",
  description: "Données collectées lors d'une commande et usage qui en est fait.",
};

export default function ConfidentialitePage() {
  return (
    <div className="mx-auto max-w-3xl space-y-10 px-6 py-16 text-sm leading-7">
      <header className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Confidentialité
        </h1>
        <p className="text-muted">
          {site.legalName} ne collecte que ce qui est nécessaire pour livrer une commande
          et répondre à une question.
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Commandes</h2>
        <p>
          Le paiement est traité par Stripe, qui recueille votre nom, votre courriel,
          votre téléphone, votre adresse de livraison et vos données de carte. Nous
          recevons tout sauf les données de carte, que nous ne voyons jamais. Ces
          informations servent à préparer, expédier et facturer la commande, ainsi
          qu&apos;au support après-vente.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Navigation</h2>
        <p>
          Ce site n&apos;utilise ni cookie publicitaire ni traceur d&apos;audience. Stripe
          dépose ses propres cookies sur sa page de paiement, pour la sécurité de la
          transaction.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Le boîtier</h2>
        <p>
          Le boîtier fonctionne sur votre réseau local. Il n&apos;envoie aucune donnée
          d&apos;entraînement vers nos serveurs : vos séances vont de votre montre à votre
          compte Garmin, comme d&apos;habitude.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Vos droits</h2>
        <p>
          Vous pouvez demander l&apos;accès, la correction ou la suppression de vos
          informations en écrivant à{" "}
          <a href={`mailto:${site.email}`} className="underline underline-offset-4">
            {site.email}
          </a>
          . Les pièces comptables sont conservées le temps exigé par la loi.
        </p>
      </section>
    </div>
  );
}
