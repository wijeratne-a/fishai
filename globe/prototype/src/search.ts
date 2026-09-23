import type { TaxonRecord } from "./types";
import { lookupWormsName } from "./worms";

function normalize(value: string): string {
  return value.trim().toLowerCase().replaceAll(/[^a-z0-9\s-]/g, " ").replaceAll(/\s+/g, " ");
}

export function displayName(taxon: TaxonRecord): string {
  return taxon.commonNames[0] ?? taxon.scientificName;
}

export function searchLocal(query: string, catalog: TaxonRecord[]): TaxonRecord[] {
  const q = normalize(query);
  if (q.length < 2) return [];
  const scored = catalog
    .map((taxon) => {
      const names = [taxon.scientificName, ...taxon.commonNames].map(normalize);
      let score = 0;
      for (const name of names) {
        if (name === q) score = Math.max(score, 100);
        else if (name.startsWith(q)) score = Math.max(score, 80);
        else if (name.includes(q)) score = Math.max(score, 50);
      }
      return { taxon, score };
    })
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score || a.taxon.scientificName.localeCompare(b.taxon.scientificName));
  return scored.slice(0, 12).map((row) => row.taxon);
}

export async function resolveSpecies(
  query: string,
  catalog: TaxonRecord[],
): Promise<{ matches: TaxonRecord[]; exact: TaxonRecord | null; remote: boolean }> {
  const local = searchLocal(query, catalog);
  const q = normalize(query);
  const exact =
    local.find((taxon) =>
      [taxon.scientificName, ...taxon.commonNames].some((name) => normalize(name) === q),
    ) ?? null;
  if (exact || local.length > 0) {
    return { matches: local, exact: exact ?? local[0] ?? null, remote: false };
  }
  const remote = await lookupWormsName(query);
  if (remote) {
    return { matches: [remote], exact: remote, remote: true };
  }
  return { matches: [], exact: null, remote: false };
}
