import type { SpeciesGroup, TaxonRecord } from "./types";

const WORMS = "https://www.marinespecies.org/rest";
const UA_NOTE = "FishAI atlas modest name lookup";
const CACHE_KEY = "fishai-worms-name-cache-v1";

let lastLookupAt = 0;
const memoryCache = new Map<string, TaxonRecord | null>();

function cacheGet(query: string): TaxonRecord | null | undefined {
  const key = query.trim().toLowerCase();
  if (memoryCache.has(key)) return memoryCache.get(key);
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return undefined;
    const parsed = JSON.parse(raw) as Record<string, TaxonRecord | null>;
    if (key in parsed) {
      memoryCache.set(key, parsed[key] ?? null);
      return parsed[key] ?? null;
    }
  } catch {
    return undefined;
  }
  return undefined;
}

function cacheSet(query: string, value: TaxonRecord | null): void {
  const key = query.trim().toLowerCase();
  memoryCache.set(key, value);
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    const parsed = raw ? (JSON.parse(raw) as Record<string, TaxonRecord | null>) : {};
    parsed[key] = value;
    sessionStorage.setItem(CACHE_KEY, JSON.stringify(parsed));
  } catch {
    /* sessionStorage may be unavailable */
  }
}

async function wormsGet(path: string): Promise<unknown> {
  const wait = Math.max(0, 350 - (Date.now() - lastLookupAt));
  if (wait) await new Promise((resolve) => window.setTimeout(resolve, wait));
  lastLookupAt = Date.now();
  const response = await fetch(`${WORMS}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (response.status === 204) return null;
  if (!response.ok) throw new Error(`WoRMS ${response.status}`);
  return response.json();
}

function groupFromRecord(record: {
  phylum?: string;
  class?: string;
  kingdom?: string;
}): SpeciesGroup {
  const phylum = record.phylum ?? "";
  const cls = record.class ?? "";
  if (phylum === "Arthropoda" || cls === "Malacostraca") return "crustacean";
  if (phylum === "Chordata") return "fish";
  if (phylum === "Mollusca") return "mollusc";
  return "other";
}

function toTaxon(record: {
  AphiaID?: number;
  valid_AphiaID?: number;
  scientificname?: string;
  status?: string;
  phylum?: string;
  class?: string;
  vernacular?: string;
}): TaxonRecord | null {
  const aphiaId = record.valid_AphiaID ?? record.AphiaID;
  const scientificName = record.scientificname;
  if (!aphiaId || !scientificName) return null;
  const group = groupFromRecord(record);
  if (group !== "fish" && group !== "crustacean" && group !== "mollusc") return null;
  return {
    aphiaId,
    scientificName,
    commonNames: record.vernacular ? [record.vernacular] : [],
    group,
    status: "name_only",
    note: `Name from WoRMS (${UA_NOTE}). Not a location estimate.`,
  };
}

export async function lookupWormsName(query: string): Promise<TaxonRecord | null> {
  const trimmed = query.trim();
  if (trimmed.length < 3) return null;
  const cached = cacheGet(trimmed);
  if (cached !== undefined) return cached;
  const encoded = encodeURIComponent(trimmed);
  try {
    const byName = (await wormsGet(
      `/AphiaRecordsByName/${encoded}?like=true&marine_only=true&offset=1`,
    )) as Array<Record<string, unknown>> | null;
    const accepted =
      byName?.find((row) => row.status === "accepted") ?? byName?.[0] ?? null;
    if (accepted) {
      const taxon = toTaxon(accepted as never);
      cacheSet(trimmed, taxon);
      return taxon;
    }
  } catch {
    /* try vernacular */
  }
  try {
    const byVernacular = (await wormsGet(
      `/AphiaRecordsByVernacular/${encoded}?like=true&offset=1`,
    )) as Array<Record<string, unknown>> | null;
    const marine = byVernacular?.find((row) => row.isMarine === 1 || row.isMarine === true);
    const pick = marine ?? byVernacular?.[0];
    if (pick) {
      const taxon = toTaxon(pick as never);
      cacheSet(trimmed, taxon);
      return taxon;
    }
  } catch {
    cacheSet(trimmed, null);
    return null;
  }
  cacheSet(trimmed, null);
  return null;
}
