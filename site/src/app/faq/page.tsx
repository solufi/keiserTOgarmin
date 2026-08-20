import type { Metadata } from "next";
import { faq } from "@/lib/content";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "FAQ",
  description: "Questions fréquentes sur le boîtier, la montre, les données et la livraison.",
};

export default function FaqPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-16">
      <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
        Questions fréquentes
      </h1>
      <div className="mt-10 space-y-4">
        {faq.map((item) => (
          <details key={item.question} className="border-line rounded-xl border p-5">
            <summary className="cursor-pointer font-medium">{item.question}</summary>
            <p className="mt-3 text-sm text-muted">{item.answer}</p>
          </details>
        ))}
      </div>
      <p className="mt-10 text-sm text-muted">
        Une question qui n&apos;est pas ici ?{" "}
        <a href={`mailto:${site.email}`} className="underline underline-offset-4">
          {site.email}
        </a>
      </p>
    </div>
  );
}
