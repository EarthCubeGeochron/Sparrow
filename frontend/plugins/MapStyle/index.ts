import { mapStyle } from "../../src/map/MapStyle";
//import { Frame, FrameChild } from "../../src/frame";
import h from "@macrostrat/hyper";

/** This is where you Add your Own Custom MapStyles!!! */

/**
 * If you want to add a Custom Style add an object to this list.
 * Add in the Name, that you want to appear on the dropdown menu on the
 * map page, after the name key and add the style key after style.
 *
 * Make sure the name is in quotes and the style also if it is a style through the MapBox API.
 * If your map style is a component add in the component without quotes.
 *
 * ex)
 *    { name: "Your Chosen Name", style: "Mapbox Style Here"}
 *
 */
export const mapStyles = [
  { name: "Standard Map", style: "mapbox://styles/mapbox/outdoors-v9" },
  { name: "DarkMode", style: "mapbox://styles/mapbox/dark-v10" },
  {
    name: "Topographic Map",
    style: "mapbox://styles/thefallingduck/cklb8itjb23wr17pd5ukdlne5",
  },
  { name: "Geologic Map", style: mapStyle },
  {
    name: "Satelite Map",
    style: "mapbox://styles/jczaplewski/cjeycrpxy1yv22rqju6tdl9xb",
  },
];

//export const mapStyles = h(FrameChild, { id: "MapStyles" });
