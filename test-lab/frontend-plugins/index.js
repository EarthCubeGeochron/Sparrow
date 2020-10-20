import { Markdown } from "@macrostrat/ui-components";
import aboutText from "./landing-text.md";
import h from "react-hyperscript";

export default {
  landingText: h(Markdown, { src: aboutText }),
};
