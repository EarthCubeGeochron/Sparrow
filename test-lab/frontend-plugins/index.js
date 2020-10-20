import { Markdown } from "@macrostrat/ui-components";
import aboutText from "./landing-text.md";
import h from "react-hyperscript";
import { SampleMap } from "plugins/globe";

export default {
  landingText: h(Markdown, { src: aboutText }),
  landingGraphic: h(SampleMap),
};
