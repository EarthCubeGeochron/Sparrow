import { hyperStyled } from "@macrostrat/hyper";
import { Frame } from "./frame";
import { InsetText } from "app/components/layout";
import styles from "./styles.module.css";
import { MapHome } from "./map";

const h = hyperStyled(styles);

const HomePage = () => {
  return h("div.homepage", [
    h(InsetText, [
      h(Frame, { id: "landingText" }),
      h(Frame, { id: "landingGraphic" }, h(MapHome)),
    ]),
  ]);
};

export { HomePage };
