import type { AppState } from "./types";

export function renderLegend(container: HTMLElement, state: AppState): void {
  const unknownOn = state.unknownMap;
  const items: { cls: string; text: string; note?: string }[] = [];

  if (state.showWillapaCells) {
    items.push({
      cls: "obs",
      text: "Measured",
      note: "A recorded value in the demo (for example water temperature).",
    });
    items.push({
      cls: "inf",
      text: "Estimate",
      note: "Demo encoding only — not a published species estimate.",
    });
    items.push({
      cls: "fc",
      text: "Forecast",
      note: "Demo encoding only — not a published forecast.",
    });
  }
  if (state.publishedCurrentEstimate) {
    items.push({
      cls: "inf",
      text: "Estimate",
      note: "Model estimate available (experimental).",
    });
  }
  if (state.publishedForecast) {
    items.push({
      cls: "fc",
      text: "Forecast",
      note: "Published forecast for a named time window.",
    });
  }
  if (state.pastReportsVisible) {
    items.push({
      cls: "past",
      text: "Past reports",
      note: "Past reports = where people recorded this species in the past, not live presence.",
    });
  }
  if (state.overlays.habitat && !unknownOn && state.showWillapaCells) {
    items.push({
      cls: "hab",
      text: "Favorable conditions",
      note: "Habitat suitability — not confirmed presence.",
    });
  }
  items.push({
    cls: "unk",
    text: "Unknown",
    note: "Stripes mean we do not know. They do not mean the ocean is empty.",
  });

  const notes: string[] = [];
  if (
    !state.showWillapaCells &&
    !state.pastReportsVisible &&
    !state.publishedCurrentEstimate &&
    !state.publishedForecast
  ) {
    notes.push("Empty globe. Imagery is Earth, not a species map. Unknown is the default.");
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
    notes.push("Gap highlight is on. Stripes = no estimate, not absence.");
  }
  if (state.dimWillapa && state.selectedTaxon) {
    notes.push("No published occurrence, abundance, movement, or forecast layer for this search.");
  }

  container.innerHTML = `
    <h2>Legend</h2>
    <div class="legend">
      ${items
        .map(
          (item) =>
            `<div class="swatch"><i class="${item.cls}" aria-hidden="true"></i><span><strong>${item.text}</strong>${
              item.note ? `<span class="legend-note">${item.note}</span>` : ""
            }</span></div>`,
        )
        .join("")}
    </div>
    ${notes.map((note) => `<p class="hint">${note}</p>`).join("")}
  `;
}
