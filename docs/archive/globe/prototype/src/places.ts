export interface NamedPlace {
  id: string;
  name: string;
  aliases: string[];
  center: [number, number];
  zoom: number;
  bounds?: [[number, number], [number, number]];
}

export const PLACES: NamedPlace[] = [
  {
    id: "earth",
    name: "Whole Earth",
    aliases: ["earth", "world", "globe", "planet"],
    center: [0, 15],
    zoom: 1.6,
  },
  {
    id: "pacific",
    name: "Pacific Ocean",
    aliases: ["pacific", "pacific ocean"],
    center: [-160, 5],
    zoom: 2.05,
  },
  {
    id: "atlantic",
    name: "Atlantic Ocean",
    aliases: ["atlantic", "atlantic ocean"],
    center: [-30, 15],
    zoom: 2.15,
  },
  {
    id: "indian",
    name: "Indian Ocean",
    aliases: ["indian ocean"],
    center: [76, -10],
    zoom: 2.35,
  },
  {
    id: "southern",
    name: "Southern Ocean",
    aliases: ["southern ocean", "antarctic ocean"],
    center: [0, -60],
    zoom: 2.4,
  },
  {
    id: "ten-thousand-islands",
    name: "Ten Thousand Islands",
    aliases: ["ten thousand islands", "thousand islands florida"],
    center: [-81.6, 25.85],
    zoom: 7.2,
  },
  {
    id: "willapa",
    name: "Willapa Bay",
    aliases: ["willapa", "willapa bay"],
    center: [-123.95, 46.55],
    zoom: 9.1,
    bounds: [
      [-124.09, 46.36],
      [-123.78, 46.735],
    ],
  },
  {
    id: "puget",
    name: "Puget Sound",
    aliases: ["puget sound", "puget"],
    center: [-122.45, 47.7],
    zoom: 7.4,
  },
  {
    id: "gulf-maine",
    name: "Gulf of Maine",
    aliases: ["gulf of maine", "maine"],
    center: [-68.4, 43.5],
    zoom: 5.8,
  },
  {
    id: "mediterranean",
    name: "Mediterranean Sea",
    aliases: ["mediterranean", "mediterranean sea"],
    center: [18, 36],
    zoom: 4.1,
  },
  {
    id: "north-sea",
    name: "North Sea",
    aliases: ["north sea"],
    center: [3.2, 56],
    zoom: 4.8,
  },
  {
    id: "coral-sea",
    name: "Coral Sea",
    aliases: ["coral sea"],
    center: [152, -16],
    zoom: 4.4,
  },
];

function normalize(value: string): string {
  return value.trim().toLowerCase().replaceAll(/[^a-z0-9\s-]/g, " ").replaceAll(/\s+/g, " ");
}

export function searchPlaces(query: string): NamedPlace[] {
  const q = normalize(query);
  if (q.length < 2) return [];
  return PLACES.filter((place) => {
    const names = [place.name, ...place.aliases].map(normalize);
    return names.some((name) => name === q || name.startsWith(q) || name.includes(q));
  }).slice(0, 6);
}

export function exactPlace(query: string): NamedPlace | null {
  const q = normalize(query);
  return (
    PLACES.find((place) => [place.name, ...place.aliases].map(normalize).includes(q)) ?? null
  );
}
