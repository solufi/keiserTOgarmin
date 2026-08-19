import Link from "next/link";
import { nav, site } from "@/lib/site";

const legal = [
  { href: "/conditions", label: "Livraison, retours et garantie" },
  { href: "/confidentialite", label: "Confidentialité" },
] as const;

export function SiteFooter() {
  return (
    <footer className="border-line mt-24 border-t">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-12 text-sm sm:flex-row sm:justify-between">
        <div className="max-w-sm space-y-2">
          <p className="font-medium">{site.legalName}</p>
          <p className="text-muted">{site.baseline}</p>
          <p className="text-muted">{site.city}</p>
          <a href={`mailto:${site.email}`} className="underline underline-offset-4">
            {site.email}
          </a>
        </div>
        <div className="flex gap-12">
          <ul className="space-y-2">
            {nav.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-muted hover:text-foreground">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
          <ul className="space-y-2">
            {legal.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-muted hover:text-foreground">
                  {item.label}
                </Link>
              </li>
            ))}
            <li>
              <a
                href={site.sourceUrl}
                className="text-muted hover:text-foreground"
                rel="noreferrer"
                target="_blank"
              >
                Code source (GPL v3)
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div className="border-line mx-auto max-w-6xl border-t px-6 py-6 text-xs text-muted">
        <p>
          Keiser, Échelon et Garmin sont des marques de leurs propriétaires respectifs.
          {` ${site.legalName} `}
          n&apos;est affilié à aucune d&apos;entre elles.
        </p>
      </div>
    </footer>
  );
}
