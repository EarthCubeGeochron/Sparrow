import { useEffect, useState } from "react";
import h from "@macrostrat/hyper";
import { NonIdealState } from "@blueprintjs/core";

export function Expired(props) {
  const { child, secondChild = h(NoSearchResults), delay } = props;
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    setTimeout(() => {
      setVisible(false);
    }, delay);
  }, [delay]);

  return visible ? child : secondChild;
}

export function NoSearchResults() {
  const description = h("div", [
    "Your search didn't match any files",
    h("br"),
    "Try searching for something else",
  ]);
  return h(NonIdealState, {
    icon: "search",
    title: "No Search Results",
    description,
  });
}
