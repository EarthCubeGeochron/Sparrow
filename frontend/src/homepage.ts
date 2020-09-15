import { hyperStyled } from "@macrostrat/hyper";
import siteContent from "site-content";
import { Frame, FrameProvider, FrameContext } from "./frame";
import { InsetText } from "app/components/layout";
// @ts-ignore
import styles from "./styles.module.css";
import { MapHome } from "./map";
import { useContext } from "react";

const h = hyperStyled(styles);

const HomePage = () => {
  const data = h(Frame, { id: "MapStyles" });
  console.log(data);
  return h("div.homepage", [
    h(InsetText, [
      h(Frame, { id: "landingText" }),
      h(Frame, { id: "landingGraphic" }, h(MapHome)),
    ]),
  ]);
};

export { HomePage };
