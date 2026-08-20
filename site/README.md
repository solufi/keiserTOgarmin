# Site transactionnel

Boutique en ligne du boîtier de conversion : pages produit en français, paiement par
**Stripe Checkout**, livraison et taxes calculées avant confirmation.

Le site est **indépendant** du logiciel embarqué ; il vit dans ce dépôt uniquement par
commodité et ne partage aucun fichier avec `linux/` ou `mcu/`.

## Stack

- [Next.js](https://nextjs.org) 16 (App Router) + TypeScript
- Tailwind CSS 4
- Stripe (Checkout hébergé + webhook)
- Déploiement visé : Vercel. Aucune base de données.

## Démarrer

```bash
cd site
npm install
cp .env.example .env.local   # puis renseigner les clés Stripe
npm run dev                  # http://localhost:3000
npm run lint
npm run build
```

## Structure

| Chemin | Rôle |
| --- | --- |
| `src/lib/site.ts` | Nom de marque, coordonnées, URL publique |
| `src/lib/catalog.ts` | Catalogue produits (prix en cents) et règles de livraison |
| `src/lib/content.ts` | Contenu éditorial : étapes, données transmises, vélos, FAQ |
| `src/lib/stripe.ts` | Client Stripe créé à la demande |
| `src/app/api/checkout` | Création de la session Stripe Checkout |
| `src/app/api/stripe/webhook` | Réception des paiements confirmés |
| `src/app/boutique` | Boutique et achat |
| `src/app/paiement/succes` | Confirmation, résumé de la commande |

Les prix ne transitent jamais par le navigateur : la requête de paiement n'envoie qu'un
`handle` de produit et une quantité, le serveur relit le prix dans `catalog.ts`.

## Variables d'environnement

| Variable | Requise | Rôle |
| --- | --- | --- |
| `STRIPE_SECRET_KEY` | pour payer | Clé secrète Stripe. Absente, le site s'affiche et le bouton d'achat renvoie une erreur explicite. |
| `STRIPE_WEBHOOK_SECRET` | pour le webhook | Vérification de signature de `/api/stripe/webhook`. |
| `NEXT_PUBLIC_SITE_URL` | recommandée | URL publique (retours de paiement, sitemap). |
| `STRIPE_AUTOMATIC_TAX` | non | `true` pour laisser Stripe Tax calculer les taxes. |
| `ORDER_WEBHOOK_URL` | non | Relais des commandes payées vers un outil externe. |

## Tester un paiement

```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook   # donne whsec_…
```

Puis, sur la boutique, carte de test `4242 4242 4242 4242`, date future, CVC quelconque.

## À décider avant la mise en ligne

- **Nom commercial** : `SpinBridge` est un nom de travail, centralisé dans
  `src/lib/site.ts` (et le logotype dans `src/components/logo.tsx`) pour être remplacé en
  un seul endroit.
- **Prix, frais de livraison et seuil de gratuité** : valeurs de départ dans
  `src/lib/catalog.ts`.
- **Courriel, ville et URL** de `src/lib/site.ts`.
- **Taxes** : activer Stripe Tax et l'immatriculation, puis `STRIPE_AUTOMATIC_TAX=true`.
- **Photographies produit** : les cartes produit sont typographiques pour l'instant.
- **Pages légales** (`/conditions`, `/confidentialite`) : rédigées comme point de départ,
  à relire avant l'ouverture des ventes.
- **Version anglaise** : le logiciel embarqué est bilingue, le site ne l'est pas encore.
