import h from "@macrostrat/hyper";
import { Frame } from "sparrow/frame";
import { ServerStatus } from "../components";

const PageFooter = (props) => {
  return h("footer", [
    h(Frame, { id: "pageFooter" }, h("div")),
    h("div.powered-by.flex-container", [
      h("p", [
        "Powered by ",
        h("b", null, h("a", { href: "https://sparrow-data.org" }, "Sparrow")),
        " ",
      ]),
      h("div.status", null, h(ServerStatus)),
      h("div.spacer"),
    ]),
  ]);
};

export { PageFooter };
