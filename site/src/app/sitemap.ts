import type { MetadataRoute } from "next";
import { site } from "@/lib/site";

const paths = [
  "/",
  "/boutique",
  "/compatibilite",
  "/installation",
  "/faq",
  "/conditions",
  "/confidentialite",
] as const;

export default function sitemap(): MetadataRoute.Sitemap {
  return paths.map((path) => ({
    url: new URL(path, site.url).toString(),
    changeFrequency: "monthly",
    priority: path === "/" ? 1 : 0.7,
  }));
}
