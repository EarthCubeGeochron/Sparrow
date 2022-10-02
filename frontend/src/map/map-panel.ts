import { compose, hyperStyled } from "@macrostrat/hyper";
import { useMapRef, MapboxMapProvider } from "@macrostrat/mapbox-react";
import { useRef, useEffect } from "react";
import { Map } from "mapbox-gl";
import styles from "./module.styl";

const h = hyperStyled(styles);

interface MapPanelProps extends mapboxgl.MapboxOptions {
  className?: string;
  children?: React.ReactNode;
  onClick?: (event: mapboxgl.MapMouseEvent, map: mapboxgl.Map) => void;
}

export function MapPanel({
  children,
  className,
  style,
  onClick,
  ...rest
}: MapPanelProps) {
  let mapRef = useMapRef() ?? useRef<Map>(null);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current == null) return;
    const map = new Map({ container: ref.current, ...rest });
    // @ts-ignore
    mapRef.current = map;
  }, [ref.current]);

  useEffect(() => {
    mapRef.current?.setStyle(style);
  }, [style]);

  useEffect(() => {
    const clickHandler = (e: mapboxgl.MapMouseEvent) => {
      onClick?.(e, mapRef.current);
    };
    mapRef.current?.on("click", clickHandler);
    return () => {
      mapRef.current?.off("click", clickHandler);
    };
  }, [onClick]);

  return h("div.map-panel", { ref, className, children });
}
