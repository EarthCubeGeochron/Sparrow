import LandingText from "./landing-text.md";
import h from "@macrostrat/hyper";
import { SampleMap } from "plugins/globe";

const MainComponent = () => {
  /** A simple React component that prints data about the site */
  return h([
    h(LandingText),
    h("h3.app-mode", [
      "Sparrow is running in ",
      h("em", null, import.meta.env.SPARROW_ENV ?? import.meta.env.MODE),
      " mode",
    ]),
  ]);
};

export default {
  landingText: h(MainComponent),
  landingGraphic: h(SampleMap),
};
