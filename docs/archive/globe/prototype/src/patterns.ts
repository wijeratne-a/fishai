/** Canvas patterns so unknown / restricted / habitat never rely on color alone. */

export type PatternId =
  | "hatch-unknown"
  | "hatch-gap"
  | "hatch-restricted"
  | "hatch-habitat"
  | "hatch-inference"
  | "hatch-forecast"
  | "hatch-depth-missing";

function imageData(
  size: number,
  draw: (ctx: CanvasRenderingContext2D) => void,
): ImageData {
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    throw new Error("Canvas 2D unavailable");
  }
  draw(ctx);
  return ctx.getImageData(0, 0, size, size);
}

export function buildPatterns(): Record<PatternId, ImageData> {
  const size = 32;
  return {
    "hatch-unknown": imageData(size, (ctx) => {
      ctx.fillStyle = "#d9d4c8";
      ctx.fillRect(0, 0, size, size);
      ctx.strokeStyle = "#4f4a43";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-4, 8);
      ctx.lineTo(8, -4);
      ctx.moveTo(0, size);
      ctx.lineTo(size, 0);
      ctx.moveTo(size - 8, size + 4);
      ctx.lineTo(size + 4, size - 8);
      ctx.stroke();
    }),
    "hatch-gap": imageData(size, (ctx) => {
      ctx.fillStyle = "#ece8df";
      ctx.fillRect(0, 0, size, size);
      ctx.strokeStyle = "#3f3b36";
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.moveTo(0, size);
      ctx.lineTo(size, 0);
      ctx.moveTo(0, 0);
      ctx.lineTo(size, size);
      ctx.stroke();
    }),
    "hatch-restricted": imageData(size, (ctx) => {
      ctx.fillStyle = "#f0d4e4";
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = "#7a3e6a";
      for (let y = 3; y < size; y += 8) {
        for (let x = 3; x < size; x += 8) {
          ctx.beginPath();
          ctx.arc(x, y, 1.6, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    }),
    "hatch-habitat": imageData(size, (ctx) => {
      ctx.fillStyle = "#cfe8dc";
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = "#00725c";
      for (let y = 4; y < size; y += 10) {
        for (let x = 4; x < size; x += 10) {
          ctx.fillRect(x, y, 3, 3);
        }
      }
    }),
    "hatch-inference": imageData(size, (ctx) => {
      ctx.fillStyle = "#f6e1b8";
      ctx.fillRect(0, 0, size, size);
      ctx.fillStyle = "#8a5a00";
      for (let y = 2; y < size; y += 6) {
        for (let x = (y % 12 === 2 ? 2 : 5); x < size; x += 6) {
          ctx.fillRect(x, y, 1.5, 1.5);
        }
      }
    }),
    "hatch-forecast": imageData(size, (ctx) => {
      ctx.fillStyle = "#d4e8f4";
      ctx.fillRect(0, 0, size, size);
      ctx.strokeStyle = "#2a6f97";
      ctx.lineWidth = 1.4;
      ctx.setLineDash([5, 4]);
      ctx.beginPath();
      ctx.moveTo(0, size * 0.35);
      ctx.lineTo(size, size * 0.35);
      ctx.moveTo(0, size * 0.7);
      ctx.lineTo(size, size * 0.7);
      ctx.stroke();
    }),
    "hatch-depth-missing": imageData(size, (ctx) => {
      ctx.fillStyle = "#e8e4dc";
      ctx.fillRect(0, 0, size, size);
      ctx.strokeStyle = "#6b655c";
      ctx.lineWidth = 1.2;
      ctx.setLineDash([2, 3]);
      ctx.beginPath();
      ctx.moveTo(0, size / 2);
      ctx.lineTo(size, size / 2);
      ctx.stroke();
    }),
  };
}
