import { escapeHtml } from "./evidence";
import type { AnswerStrip } from "./types";

export function emptyAnswer(): AnswerStrip {
  return {
    species: "No species selected",
    whereNow: "Search a species or pick a place.",
    soon: "No forecast issued.",
    howSure: "None",
    depth: "Depth unknown",
    why: "Nothing has been asked yet.",
    thisIsNot: "Live tracking, a fishing map, or a count of animals.",
    whatShown: "Empty globe. No species layer. Unknown is the scientific status.",
    scientificStatus: "Unknown.",
    targetsNote:
      "Observed presence, occurrence probability, relative abundance, and movement are not issued. Habitat is not a presence claim. Unknown is first-class.",
  };
}

export function renderAnswerStrip(container: HTMLElement, strip: AnswerStrip): void {
  container.innerHTML = `
    <div class="answer-grid">
      <div><span class="k">Species</span><strong>${escapeHtml(strip.species)}</strong></div>
      <div><span class="k">Where now</span><p>${escapeHtml(strip.whereNow)}</p></div>
      <div><span class="k">Soon</span><p>${escapeHtml(strip.soon)}</p></div>
      <div><span class="k">How sure</span><p>${escapeHtml(strip.howSure)}</p></div>
      <div><span class="k">Depth</span><p>${escapeHtml(strip.depth)}</p></div>
      <div class="answer-why"><span class="k">Why</span><p>${escapeHtml(strip.why)}</p></div>
      <div class="answer-shown"><span class="k">What is shown</span><p>${escapeHtml(strip.whatShown ?? "No species layer.")}</p></div>
      <div class="answer-status"><span class="k">Scientific status</span><p>${escapeHtml(strip.scientificStatus ?? "Unknown.")}</p></div>
      <div class="answer-not"><span class="k">This is not</span><p>${escapeHtml(strip.thisIsNot)}</p></div>
    </div>
    ${
      strip.targetsNote
        ? `<p class="targets-note">${escapeHtml(strip.targetsNote)}</p>`
        : ""
    }
    ${
      strip.quantityNote
        ? `<p class="quantity-chip">${escapeHtml(strip.quantityNote)}</p>`
        : ""
    }
    ${
      strip.supportLine
        ? `<p class="support-line">${escapeHtml(strip.supportLine)}</p>`
        : ""
    }
  `;
}

export function composeLiveSentence(strip: AnswerStrip): string {
  return `${strip.species}. Where now: ${strip.whereNow} Soon: ${strip.soon} How sure: ${strip.howSure}. Depth: ${strip.depth}. Why: ${strip.why}`;
}
