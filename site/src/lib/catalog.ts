/**
 * Catalogue produits : source unique de vérité pour l'affichage et pour les
 * lignes de paiement Stripe. Les prix sont en cents, comme dans l'API Stripe,
 * afin de n'avoir aucune conversion à faire côté serveur.
 */

export const currency = "cad";

export type Product = {
  /** Identifiant stable, utilisé dans les URL et dans les requêtes de paiement. */
  handle: string;
  sku: string;
  title: string;
  tagline: string;
  priceCents: number;
  /** Points forts affichés sur la carte produit. */
  includes: readonly string[];
  description: string;
  /** Un seul produit porte la mention « recommandé ». */
  featured?: boolean;
  /** Quantité maximale commandable en une fois. */
  maxQuantity: number;
};

export const products: readonly Product[] = [
  {
    handle: "pont-ant",
    sku: "SB-ANT-01",
    title: "Pont SpinBridge — Édition ANT+",
    tagline: "Le montage le plus stable, plusieurs appareils à la fois.",
    priceCents: 34900,
    includes: [
      "Boîtier Raspberry Pi assemblé, logiciel préinstallé et configuré",
      "Clé USB ANT+ Garmin d'origine (010-01058-00)",
      "Alimentation et carte mémoire incluses",
      "Deux capteurs vus par la montre : puissance/cadence et vitesse/distance",
    ],
    description:
      "La liaison ANT+ est plus stable que le Bluetooth et permet à plusieurs appareils de capter le vélo en même temps. Le boîtier arrive configuré : vous le branchez, vous appairez la montre une fois, vous pédalez.",
    featured: true,
    maxQuantity: 5,
  },
  {
    handle: "pont-bluetooth",
    sku: "SB-BLE-01",
    title: "Pont SpinBridge — Édition Bluetooth",
    tagline: "Tout ce qu'il faut pour enregistrer puissance et cadence.",
    priceCents: 27900,
    includes: [
      "Boîtier Raspberry Pi assemblé, logiciel préinstallé et configuré",
      "Alimentation et carte mémoire incluses",
      "Un capteur de puissance vu par la montre",
      "Passage à l'ANT+ possible plus tard en ajoutant la clé USB",
    ],
    description:
      "La montre voit un capteur de puissance Bluetooth standard, ce qui suffit pour enregistrer puissance et cadence dans l'activité. Aucun accessoire supplémentaire à acheter.",
    maxQuantity: 5,
  },
  {
    handle: "cle-ant",
    sku: "SB-DGL-01",
    title: "Clé USB ANT+ Garmin",
    tagline: "Pour faire passer un pont Bluetooth en ANT+.",
    priceCents: 7900,
    includes: [
      "Clé Garmin d'origine, référence 010-01058-00",
      "Reconnue automatiquement par le boîtier",
      "Les clés d'autres marques ne fonctionnent pas",
    ],
    description:
      "Accessoire seul, pour les clients qui possèdent déjà un pont en édition Bluetooth et veulent la liaison ANT+.",
    maxQuantity: 5,
  },
] as const;

export function findProduct(handle: string): Product | undefined {
  return products.find((product) => product.handle === handle);
}

/** Livraison à tarif unique, offerte au-delà d'un seuil. */
export const shipping = {
  label: "Livraison suivie",
  flatRateCents: 1500,
  freeAboveCents: 30000,
  countries: ["CA", "US"],
  deliveryDaysMin: 3,
  deliveryDaysMax: 8,
} as const;

export function shippingCents(subtotalCents: number): number {
  return subtotalCents >= shipping.freeAboveCents ? 0 : shipping.flatRateCents;
}

export function formatPrice(cents: number): string {
  return new Intl.NumberFormat("fr-CA", {
    style: "currency",
    currency: currency.toUpperCase(),
    maximumFractionDigits: cents % 100 === 0 ? 0 : 2,
  }).format(cents / 100);
}
