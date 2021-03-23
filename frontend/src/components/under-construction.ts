import { NonIdealState } from "@blueprintjs/core";
import h from "@macrostrat/hyper";

const UnderConstruction = function(props) {
  const { name } = props;
  const rest = " view is not yet implemented. Sorry!";
  let desc = "This" + rest;
  if (name != null) {
    desc = h(["The ", h("b", name), rest]);
  }
  return h(NonIdealState, {
    title: "Under construction",
    description: desc,
    icon: "build",
  });
};

export { UnderConstruction };
