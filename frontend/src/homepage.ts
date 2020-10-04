import { hyperStyled } from "@macrostrat/hyper";
import { Frame } from "./frame";
import { InsetText } from "app/components/layout";
// @ts-ignore
import styles from "./styles.module.css";
import loadable from "@loadable/component";

import { SampleMap } from "../plugins/globe";
import { useContext } from "react";


const MapHome = loadable(async function() {
  const module = await import("./map");
  return module.MapHome;
});

const h = hyperStyled(styles);

const HomePage = () => {
  return h("div.homepage", [
    h(InsetText, [
      h(
        Frame,
        { id: "landingText" },
        "This is where your lab's description text can go"
      ),
      h(Frame, { id: "landingGraphic" }, h(MapHome)),
    ]),
  ]);
};

export { HomePage };
