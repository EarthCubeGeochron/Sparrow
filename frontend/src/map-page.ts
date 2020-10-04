import h from "@macrostrat/hyper";
import { Frame } from "./frame";
import loadable from "@loadable/component";

const MapPage = loadable(async function() {
  const module = await import("./map");
  return module.MapPage;
});

const Map_Page = () => {
  return h("div", [h(Frame), { id: "mapPageComponent" }, h(MapPage)]);
};

export { Map_Page };
