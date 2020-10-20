import { Markdown } from "@macrostrat/ui-components";
import aboutText from "./landing-text.md";
import h from "react-hyperscript";
import { SampleMap } from "plugins/globe";

const MainComponent = () => {
  /** A simple React component that prints data about the site */
  return h([
    h(Markdown, { src: aboutText }),
    h("h3.app-mode", [
      "Sparrow is running in ",
      h("em", null, process.env.SPARROW_ENV),
      " mode",
    ]),
  ]);
};

export default {
  landingText: h(MainComponent),
  landingGraphic: h(SampleMap),
};
