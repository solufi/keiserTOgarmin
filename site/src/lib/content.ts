/** Contenu éditorial du site, repris du guide d'installation du dépôt. */

export const steps = [
  {
    title: "Branchez le boîtier",
    body: "Il tient dans la main et se pose sur le guidon ou au sol. Une prise USB suffit ; aucun câble vers le vélo, aucun capteur à coller.",
  },
  {
    title: "Choisissez votre vélo",
    body: "À la première mise en route, une page web s'ouvre depuis votre téléphone : vous pédalez, le vélo dont la cadence bouge est le vôtre, vous le sélectionnez.",
  },
  {
    title: "Appairez la montre une fois",
    body: "Sur la montre : Paramètres → Capteurs et accessoires → Ajouter. Ensuite elle retrouve le boîtier seule, à chaque séance.",
  },
  {
    title: "Pédalez",
    body: "Le boîtier démarre tout seul au branchement. Une trentaine de secondes plus tard, la montre enregistre la séance.",
  },
] as const;

export const metrics = [
  {
    name: "Puissance",
    detail: "Lue directement sur la console du vélo, en watts.",
  },
  {
    name: "Cadence",
    detail: "Lue directement sur la console du vélo, en tours par minute.",
  },
  {
    name: "Vitesse et distance",
    detail:
      "Calculées à partir de la puissance par un modèle physique : plausibles, mais pas mesurées par le vélo.",
  },
  {
    name: "Fréquence cardiaque",
    detail:
      "Elle vient de votre montre ou de votre ceinture, comme d'habitude. Le boîtier n'y touche pas.",
  },
] as const;

export const bikes = [
  {
    name: "Keiser M3i",
    status: "Compatible",
    note: "Console d'origine allumée, rien à ajouter sur le vélo.",
    available: true,
  },
  {
    name: "Échelon",
    status: "En préparation",
    note: "Prochain vélo visé. Écrivez-nous pour être prévenu et tester une version d'avance.",
    available: false,
  },
  {
    name: "Autre vélo de salle",
    status: "Sur demande",
    note: "Dites-nous le modèle : s'il diffuse ses données, il peut être ajouté au boîtier par mise à jour.",
    available: false,
  },
] as const;

export const watches = [
  "Forerunner",
  "Fenix",
  "Epix",
  "Venu",
  "Vivoactive",
  "Edge",
] as const;

export const faq = [
  {
    question: "Faut-il installer quelque chose sur la montre ?",
    answer:
      "Non. La montre voit un capteur de puissance standard : aucune application, aucun réglage particulier. Réglez simplement la circonférence de roue à 2096 mm lors de l'appairage.",
  },
  {
    question: "Est-ce que cela modifie le vélo ?",
    answer:
      "Aucunement. Le boîtier écoute le signal que la console du vélo diffuse déjà. Rien n'est branché, collé ni démonté sur le vélo, ce qui compte en salle ou en location.",
  },
  {
    question: "Bluetooth ou ANT+ : que choisir ?",
    answer:
      "Le Bluetooth suffit pour enregistrer puissance et cadence. L'ANT+ est plus stable et permet à plusieurs appareils de capter le vélo en même temps ; la montre voit alors deux capteurs, l'un pour la puissance et la cadence, l'autre pour la vitesse et la distance.",
  },
  {
    question: "Et si je n'ai pas de réseau Wi-Fi dans la salle ?",
    answer:
      "Le boîtier crée son propre réseau lorsqu'il n'en trouve aucun de connu : vous vous y connectez avec le téléphone pour le configurer. Une fois réglé, il fonctionne sans Wi-Fi ni téléphone.",
  },
  {
    question: "La vitesse affichée est-elle exacte ?",
    answer:
      "Le vélo ne transmet pas de vitesse : elle est estimée à partir de la puissance par un modèle physique. L'ordre de grandeur est juste, mais ce n'est pas une mesure.",
  },
  {
    question: "Les mises à jour sont-elles payantes ?",
    answer:
      "Non. Un bouton de mise à jour est intégré à la page de configuration, et le logiciel est libre : les vélos ajoutés plus tard arrivent par simple mise à jour.",
  },
  {
    question: "Puis-je le construire moi-même ?",
    answer:
      "Oui, et c'est assumé : le logiciel est publié sous licence GNU GPL v3. Ce que nous vendons, c'est le matériel choisi, assemblé, préconfiguré et garanti, ainsi que le support.",
  },
  {
    question: "Quel est le délai de livraison ?",
    answer:
      "Les boîtiers sont assemblés à la commande et expédiés du Canada, généralement sous trois à huit jours ouvrables selon la destination.",
  },
] as const;
