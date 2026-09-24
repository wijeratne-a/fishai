import type { FlyToOptions, LngLatBoundsLike, Map as MapLibreMap, MapOptions } from "maplibre-gl";

export type MapProjectionMode = "globe" | "mercator";

export const CAMERA = {
  WORLD_CENTER: [0, 15] as [number, number],
  WORLD_ZOOM: 1.6,
  WORLD_PITCH: 28,
  MIN_ZOOM: 0.8,
  MAX_ZOOM: 12,
  MIN_PITCH: 0,
  MAX_PITCH: 60,
  GLOBE_TILT_UNTIL_ZOOM: 4,
  SELECT_DRAG_PX: 7,
};

export interface CameraSnapshot {
  center: [number, number];
  zoom: number;
  pitch: number;
  bearing: number;
}

export function prefersReducedMotion(): boolean {
  return typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

export function motionMs(preferred = 900): number {
  return prefersReducedMotion() ? 0 : preferred;
}

export function mapCameraOptions(projectionMode: MapProjectionMode): Partial<MapOptions> {
  return {
    center: CAMERA.WORLD_CENTER,
    zoom: CAMERA.WORLD_ZOOM,
    pitch: 0,
    bearing: 0,
    minZoom: CAMERA.MIN_ZOOM,
    maxZoom: CAMERA.MAX_ZOOM,
    minPitch: CAMERA.MIN_PITCH,
    maxPitch: CAMERA.MAX_PITCH,
    attributionControl: false,
    cooperativeGestures: false,
    dragRotate: true,
    pitchWithRotate: true,
    touchPitch: true,
    doubleClickZoom: true,
    keyboard: true,
    scrollZoom: true,
    boxZoom: true,
    renderWorldCopies: projectionMode === "mercator",
    fadeDuration: prefersReducedMotion() ? 0 : 280,
    trackResize: true,
    dragPan: {
      linearity: 0.26,
      maxSpeed: 1100,
      deceleration: 3000,
    },
    canvasContextAttributes: {
      antialias: true,
      powerPreference: "high-performance",
    },
  };
}

export function snapshotCamera(map: MapLibreMap): CameraSnapshot {
  const center = map.getCenter();
  return {
    center: [center.lng, center.lat],
    zoom: map.getZoom(),
    pitch: map.getPitch(),
    bearing: map.getBearing(),
  };
}

export function interruptCamera(map: MapLibreMap): void {
  map.stop();
}

export function bindFlightInterrupt(map: MapLibreMap): void {
  const stop = (): void => {
    map.stop();
  };
  map.on("dragstart", stop);
  map.on("rotatestart", stop);
  map.on("pitchstart", stop);
  map.on("wheel", stop);
}

export function tuneNativeHandlers(map: MapLibreMap): void {
  map.scrollZoom.setWheelZoomRate(1 / 520);
  map.scrollZoom.setZoomRate(1 / 110);
  map.scrollZoom.enable();
  map.dragPan.enable({
    linearity: 0.26,
    maxSpeed: 1100,
    deceleration: 3000,
  });
  map.doubleClickZoom.enable();
  map.dragRotate.enable();
  map.touchPitch.enable();
  map.touchZoomRotate.enable();
  map.keyboard.enable();
}

export function bindPointerSelectGuard(
  map: MapLibreMap,
  thresholdPx = CAMERA.SELECT_DRAG_PX,
): { wasDrag: () => boolean } {
  let origin: { x: number; y: number } | null = null;
  let dragged = false;
  const canvas = map.getCanvas();
  canvas.addEventListener("pointerdown", (event) => {
    origin = { x: event.clientX, y: event.clientY };
    dragged = false;
  });
  canvas.addEventListener("pointermove", (event) => {
    if (!origin) return;
    if (Math.hypot(event.clientX - origin.x, event.clientY - origin.y) > thresholdPx) {
      dragged = true;
    }
  });
  canvas.addEventListener("pointerup", () => {
    origin = null;
  });
  canvas.addEventListener("pointercancel", () => {
    origin = null;
    dragged = true;
  });
  return {
    wasDrag: () => dragged,
  };
}

export function globePitchForZoom(mode: MapProjectionMode, zoom: number, currentPitch: number): number {
  if (mode !== "globe") return 0;
  if (zoom < CAMERA.GLOBE_TILT_UNTIL_ZOOM) return Math.max(currentPitch, CAMERA.WORLD_PITCH * 0.65);
  return currentPitch;
}

export function flyToView(map: MapLibreMap, view: CameraSnapshot, duration = 800): void {
  const camera = {
    center: view.center,
    zoom: view.zoom,
    pitch: view.pitch,
    bearing: view.bearing,
  };
  if (prefersReducedMotion() || motionMs(duration) === 0) {
    map.jumpTo(camera);
    return;
  }
  const options: FlyToOptions = { ...camera, duration: motionMs(duration), essential: true };
  map.flyTo(options);
}

export function flyHome(map: MapLibreMap, mode: MapProjectionMode): void {
  flyToView(map, {
    center: CAMERA.WORLD_CENTER,
    zoom: CAMERA.WORLD_ZOOM,
    pitch: mode === "globe" ? CAMERA.WORLD_PITCH : 0,
    bearing: 0,
  }, 900);
}

export function resetNorth(map: MapLibreMap, mode: MapProjectionMode): void {
  const duration = motionMs(420);
  const pitch = mode === "globe" && map.getZoom() < CAMERA.GLOBE_TILT_UNTIL_ZOOM ? CAMERA.WORLD_PITCH : map.getPitch();
  if (duration === 0) {
    map.jumpTo({ bearing: 0, pitch });
    return;
  }
  map.easeTo({ bearing: 0, pitch, duration });
}

export function resetTilt(map: MapLibreMap, mode: MapProjectionMode): void {
  const duration = motionMs(380);
  const pitch = mode === "globe" && map.getZoom() < CAMERA.GLOBE_TILT_UNTIL_ZOOM ? CAMERA.WORLD_PITCH : 0;
  if (duration === 0) {
    map.jumpTo({ pitch, bearing: map.getBearing() });
    return;
  }
  map.easeTo({ pitch, duration });
}

export function fitRegion(
  map: MapLibreMap,
  bounds: LngLatBoundsLike,
  mode: MapProjectionMode,
  maxZoom = 10.2,
): void {
  map.fitBounds(bounds, {
    padding: { top: 88, bottom: 72, left: 48, right: 48 },
    duration: motionMs(880),
    maxZoom,
    pitch: mode === "globe" ? 42 : 0,
    bearing: 0,
    essential: true,
  });
}

export class CameraHistory {
  private readonly stack: CameraSnapshot[] = [];

  push(map: MapLibreMap): void {
    this.stack.push(snapshotCamera(map));
    if (this.stack.length > 24) this.stack.shift();
  }

  back(map: MapLibreMap): boolean {
    const previous = this.stack.pop();
    if (!previous) return false;
    flyToView(map, previous, 620);
    return true;
  }
}

/** Recast the globe transform after the container size actually changes. */
export function recastViewport(map: MapLibreMap): void {
  const container = map.getContainer();
  const width = container.clientWidth;
  const height = container.clientHeight;
  if (width < 2 || height < 2) return;
  map.resize();
  const canvas = map.getCanvas();
  const sliver =
    canvas.clientWidth < width * 0.5 ||
    canvas.clientHeight < height * 0.5 ||
    canvas.clientWidth < 64 ||
    canvas.clientHeight < 64;
  if (!sliver || map.isMoving()) return;
  const center = map.getCenter();
  map.jumpTo({
    center: [center.lng, center.lat],
    zoom: map.getZoom(),
    bearing: map.getBearing(),
    pitch: map.getPitch(),
  });
}

export function scheduleRecast(map: MapLibreMap): void {
  requestAnimationFrame(() => {
    recastViewport(map);
    requestAnimationFrame(() => recastViewport(map));
  });
}
