/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "react-hyperscript";
import { AppNavbar, NavButton } from "app/components/navbar";
import { MapHome } from "./map/index";
import { Frame } from "./frame";
import { InsetText } from "app/layout";
import "./styles.modules.css";

const HomePage = () =>
  h("div.homepage", [
    h(InsetText, null, [
      h(Frame, { id: "landingText" }, "Landing page text goes here."),
      h(Frame, { id: "landingGraphic" }, h(MapHome)),
    ]),
  ]);

export { HomePage };
