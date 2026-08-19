/**
 * Nommage et coordonnées de la marque. Le nom commercial est volontairement
 * indépendant des marques de vélos et de montres : le catalogue doit pouvoir
 * accueillir d'autres vélos (Échelon…) sans renommer le produit.
 */
export const site = {
  /** Raison sociale, mentions légales et reçus Stripe. */
  legalName: "SpinBridge",
  /** Nom de marque tel qu'il s'écrit dans les phrases. */
  name: "SpinBridge",
  baseline: "Votre vélo de spinning parle enfin à votre montre",
  description:
    "Un boîtier plug and play qui écoute votre vélo de spinning et le retransmet à votre montre Garmin comme un capteur de puissance standard. Puissance, cadence, vitesse et distance enregistrées dans l'activité, sans rien installer sur la montre.",
  email: "bonjour@spinbridge.example",
  city: "Québec, Canada",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "https://spinbridge.example",
  /** Dépôt du logiciel embarqué, publié sous GNU GPL v3. */
  sourceUrl: "https://github.com/solufi/keiserTOgarmin",
} as const;

export const nav = [
  { href: "/boutique", label: "Boutique" },
  { href: "/compatibilite", label: "Compatibilité" },
  { href: "/installation", label: "Installation" },
  { href: "/faq", label: "FAQ" },
] as const;
