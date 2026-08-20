import type { Metadata } from "next";
import { formatPrice, shipping } from "@/lib/catalog";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Livraison, retours et garantie",
  description:
    "Délais d'expédition, frais de livraison, droit de retour et garantie du matériel.",
};

export default function ConditionsPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-10 px-6 py-16 text-sm leading-7">
      <header className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Livraison, retours et garantie
        </h1>
        <p className="text-muted">
          Ces conditions s&apos;appliquent aux commandes passées sur ce site auprès de{" "}
          {site.legalName}, {site.city}.
        </p>
      </header>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Prix et paiement</h2>
        <p>
          Les prix sont affichés en dollars canadiens. Les taxes applicables et les frais
          de livraison sont calculés et affichés avant la confirmation du paiement. Le
          paiement est traité par Stripe : nous ne voyons ni ne conservons vos données de
          carte.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Expédition</h2>
        <p>
          Les boîtiers sont assemblés et configurés à la commande, puis expédiés du Canada
          avec suivi. Comptez de {shipping.deliveryDaysMin} à {shipping.deliveryDaysMax}{" "}
          jours ouvrables après la commande. La livraison coûte{" "}
          {formatPrice(shipping.flatRateCents)} et devient gratuite dès{" "}
          {formatPrice(shipping.freeAboveCents)} d&apos;achat. Nous livrons au Canada et
          aux États-Unis ; les droits et taxes d&apos;importation éventuels restent à la
          charge du destinataire.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Retours</h2>
        <p>
          Le matériel peut être retourné dans les 30 jours suivant la réception, complet
          et en état de revente, pour un remboursement du prix des articles. Les frais de
          retour sont à votre charge, sauf en cas d&apos;erreur de notre part ou de
          produit défectueux. Écrivez à{" "}
          <a href={`mailto:${site.email}`} className="underline underline-offset-4">
            {site.email}
          </a>{" "}
          avant tout envoi afin d&apos;obtenir les instructions de retour.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Garantie</h2>
        <p>
          Le matériel est garanti un an contre les défauts de fabrication : réparation ou
          remplacement à notre choix. La garantie ne couvre ni les dommages liés à un
          usage anormal, ni l&apos;usure normale, ni les modifications matérielles.
        </p>
        <p>
          Le logiciel embarqué est un logiciel libre distribué sous licence GNU GPL v3,
          &laquo; en l&apos;état &raquo;, sans garantie. Les mises à jour sont gratuites.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Compatibilité et usage</h2>
        <p>
          Le boîtier lit le signal diffusé par la console du vélo : il ne modifie pas le
          vélo et ne s&apos;y branche pas. La vitesse et la distance sont estimées à
          partir de la puissance ; ce ne sont pas des mesures. Les vélos et appareils pris
          en charge sont listés sur la page Compatibilité au moment de la commande.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Marques citées</h2>
        <p>
          Keiser, Échelon, Garmin et ANT+ sont des marques de leurs propriétaires
          respectifs, citées à des fins de compatibilité.
          {` ${site.legalName} `}
          n&apos;est affilié à aucune d&apos;entre elles et n&apos;est pas un revendeur
          agréé.
        </p>
      </section>
    </div>
  );
}
