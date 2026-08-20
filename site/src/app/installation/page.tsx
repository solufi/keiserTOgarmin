import type { Metadata } from "next";
import { steps } from "@/lib/content";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Installation",
  description:
    "Quatre étapes, une dizaine de minutes la première fois, puis plus rien à faire.",
};

const details = [
  {
    title: "Appairage de la montre",
    body: "Paramètres → Capteurs et accessoires → Ajouter. En Bluetooth, ajoutez un capteur de puissance. En ANT+, ajoutez le capteur de puissance puis, séparément, le capteur de vitesse. Dans les deux cas, réglez la circonférence de roue à 2096 mm.",
  },
  {
    title: "Page de configuration",
    body: "Le boîtier expose une page web sur votre réseau local, en français ou en anglais. On y choisit le vélo, le mode de sortie, et on y suit le journal en direct pour vérifier que les données montent.",
  },
  {
    title: "Wi-Fi sans écran ni clavier",
    body: "S'il ne trouve aucun réseau connu, le boîtier crée le sien après une quarantaine de secondes. Vous vous y connectez avec le téléphone, vous indiquez votre Wi-Fi, et le réseau de secours disparaît.",
  },
  {
    title: "Mises à jour",
    body: "Un bouton sur la page de configuration récupère la dernière version et redémarre les services. Votre configuration est conservée. Les vélos ajoutés plus tard arrivent par ce chemin.",
  },
] as const;

export default function InstallationPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Installation</h1>
      <p className="mt-4 text-muted">
        Le boîtier arrive configuré : le logiciel, le service de démarrage automatique et
        les réglages de la liaison sont déjà en place. Il reste à choisir votre vélo et à
        appairer la montre, une seule fois.
      </p>

      <ol className="mt-10 space-y-6">
        {steps.map((step, index) => (
          <li key={step.title} className="border-line rounded-xl border p-5">
            <p className="text-sm text-muted">Étape {index + 1}</p>
            <h2 className="mt-1 font-medium">{step.title}</h2>
            <p className="mt-2 text-sm text-muted">{step.body}</p>
          </li>
        ))}
      </ol>

      <h2 className="mt-16 text-xl font-semibold">Bon à savoir</h2>
      <dl className="mt-6 space-y-5">
        {details.map((detail) => (
          <div key={detail.title}>
            <dt className="font-medium">{detail.title}</dt>
            <dd className="mt-1 text-sm text-muted">{detail.body}</dd>
          </div>
        ))}
      </dl>

      <h2 className="mt-16 text-xl font-semibold">Logiciel libre</h2>
      <p className="mt-4 text-sm text-muted">
        Le logiciel embarqué est publié sous licence GNU GPL v3 et son code est public :{" "}
        <a
          href={site.sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-4"
        >
          {site.sourceUrl.replace("https://", "")}
        </a>
        . Vous pouvez donc l&apos;installer vous-même sur votre propre matériel. Ce que
        nous vendons, c&apos;est un ensemble choisi, assemblé, préconfiguré, garanti et
        accompagné.
      </p>
    </div>
  );
}
