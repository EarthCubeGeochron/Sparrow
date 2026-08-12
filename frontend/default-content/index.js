import AboutText from "./about.md";
import h from "@macrostrat/hyper";

const siteTitle = import.meta.env.SPARROW_LAB_NAME ?? "Fab Lab \u{1F52C} \u{1F308}";

export default {
  landingText: h(AboutText),
  siteTitle,
};
