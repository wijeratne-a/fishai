import type { FixtureCollection, PastReportsSummary } from "./types";

/** Taxa we never draw as a public past-report grid (listed / aggregation-sensitive). */
const WITHHOLD_APHIA = new Set<number>([
  105838, // Carcharodon carcharias — withhold native grain
]);

const MIN_CELL_N = 3;
const MAX_CELLS = 80;
const PACE_MS = 350;

const memoryCache = new Map<number, PastReportsResult>();
let lastLookupAt = 0;

async function obisGet(url: string): Promise<unknown> {
  const wait = Math.max(0, PACE_MS - (Date.now() - lastLookupAt));
  if (wait) await new Promise((resolve) => window.setTimeout(resolve, wait));
  lastLookupAt = Date.now();
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) throw new Error(`OBIS ${response.status}`);
  return response.json();
}

function yearSpanFromRows(rows: Array<{ year?: number }>): string | null {
  const years = rows
    .map((row) => row.year)
    .filter((year): year is number => typeof year === "number" && year > 0)
    .sort((a, b) => a - b);
  if (years.length === 0) return null;
  const first = years[0];
  const last = years[years.length - 1];
  return first === last ? String(first) : `${first}–${last}`;
}

export interface PastReportsResult {
  summary: PastReportsSummary;
  collection: FixtureCollection<{ n: number; label: string }> | null;
}

export async function fetchPastReports(
  scientificName: string,
  aphiaId: number,
): Promise<PastReportsResult> {
  const cached = memoryCache.get(aphiaId);
  if (cached) return cached;

  const source = "OBIS occurrence API (official), coarsened ~1° grid";
  const licenseNote =
    "OBIS compiles many datasets. This view names the compiler (OBIS) and is a count of past reports, not where animals are now. Source-dataset licenses vary; commercial-restricted sets are not shown as harvest maps.";

  if (WITHHOLD_APHIA.has(aphiaId)) {
    const withheld: PastReportsResult = {
      collection: null,
      summary: {
        scientificName,
        total: null,
        yearSpan: null,
        cellsDrawn: 0,
        withheld: true,
        source,
        licenseNote: "Locations withheld. Listed or sensitive taxon.",
      },
    };
    memoryCache.set(aphiaId, withheld);
    return withheld;
  }

  const name = encodeURIComponent(scientificName);
  try {
    const countJson = (await obisGet(
      `https://api.obis.org/v3/occurrence?scientificname=${name}&size=0`,
    )) as { total?: number };
    const total = typeof countJson.total === "number" ? countJson.total : null;

    let yearSpan: string | null = null;
    try {
      const years = (await obisGet(
        `https://api.obis.org/v3/statistics/years?scientificname=${name}`,
      )) as Array<{ year?: number }>;
      yearSpan = yearSpanFromRows(years);
    } catch {
      yearSpan = null;
    }

    if (!total || total < MIN_CELL_N) {
      const empty: PastReportsResult = {
        collection: null,
        summary: {
          scientificName,
          total: total ?? 0,
          yearSpan,
          cellsDrawn: 0,
          withheld: false,
          source,
          licenseNote,
        },
      };
      memoryCache.set(aphiaId, empty);
      return empty;
    }

    const grid = (await obisGet(
      `https://api.obis.org/v3/occurrence/grid/1?scientificname=${name}`,
    )) as {
      type?: string;
      features?: Array<{
        type: string;
        properties?: { n?: number };
        geometry: { type: string; coordinates: unknown };
      }>;
    };

    const features = (grid.features ?? [])
      .filter((feature) => (feature.properties?.n ?? 0) >= MIN_CELL_N)
      .slice(0, MAX_CELLS)
      .map((feature, index) => ({
        type: "Feature" as const,
        properties: {
          n: feature.properties?.n ?? 0,
          label: `Past reports cell ${index + 1}`,
        },
        geometry: feature.geometry,
      }));

    const result: PastReportsResult = {
      collection:
        features.length > 0
          ? { type: "FeatureCollection", name: "obis_past_reports_coarse", features }
          : null,
      summary: {
        scientificName,
        total,
        yearSpan,
        cellsDrawn: features.length,
        withheld: false,
        source,
        licenseNote,
      },
    };
    memoryCache.set(aphiaId, result);
    return result;
  } catch (error) {
    const message = error instanceof Error ? error.message : "OBIS request failed";
    return {
      collection: null,
      summary: {
        scientificName,
        total: null,
        yearSpan: null,
        cellsDrawn: 0,
        withheld: false,
        source,
        licenseNote,
        error: message,
      },
    };
  }
}
