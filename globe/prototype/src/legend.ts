import type { AppState } from "./types";

export function renderLegend(container: HTMLElement, state: AppState): void {
  const unknownOn = state.unknownMap;
  const items: { cls: string; text: string }[] = [];

  if (state.showWillapaCells) {
    items.push({ cls: "obs", text: "Confirmed observation (demo / measured value)" });
    items.push({ cls: "inf", text: "Guessed (demo encoding — not a published estimate)" });
    items.push({ cls: "fc", text: "Forecast (demo encoding — not a published forecast)" });
  }
  if (state.publishedCurrentEstimate) {
    items.push({ cls: "inf", text: "Current estimate (published)" });
  }
  if (state.publishedForecast) {
    items.push({ cls: "fc", text: "Forecast (published)" });
  }
  if (state.pastReportsVisible) {
    items.push({ cls: "past", text: "Historical pattern — past reports, not now" });
  }
  if (state.overlays.habitat && !unknownOn && state.showWillapaCells) {
    items.push({ cls: "hab", text: "Favorable conditions — not confirmed presence" });
  }
  items.push({ cls: "unk", text: "Unknown — not absence" });

  const notes: string[] = [];
  if (!state.showWillapaCells && !state.pastReportsVisible && !state.publishedCurrentEstimate && !state.publishedForecast) {
    notes.push("Empty globe. Imagery is Earth, not a species map.");
  }
  if (state.overlays.sst && !unknownOn) {
    notes.push("Blue–yellow dots are water-skin temperature in °C — not animals.");
  }
  if (state.overlays.sst && unknownOn) {
    notes.push("Gap view hides temperature dots so they are not mistaken for animals.");
  }
  if (state.overlays.habitat && !unknownOn) {
    notes.push("Brown marks favorable conditions — not confirmed species presence.");
  }
  if (state.overlays.density && state.expert) {
    notes.push("Numbers are sample rows, not a headcount.");
  }
  if (unknownOn) {
    notes.push("Stripes mean we do not have an estimate. They do not mean the ocean is empty.");
  }
  if (state.pastReportsVisible) {
    notes.push("Past reports are a historical pattern. They are not measured-now and not a forecast.");
  }
  if (state.dimWillapa) {
    notes.push("No published occurrence, abundance, movement, or forecast layer for this search.");
  }

  container.innerHTML = `
    <h2>Legend</h2>
    <div class="legend">
      ${items
        .map(
          (item) =>
            `<div class="swatch"><i class="${item.cls}" aria-hidden="true"></i><span>${item.text}</span></div>`,
        )
        .join("")}
    </div>
    ${notes.map((note) => `<p class="hint">${note}</p>`).join("")}
  `;
}
