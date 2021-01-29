import * as React from "react";
import h from "@macrostrat/hyper";
import { Card, Dialog, Divider } from "@blueprintjs/core";
import { buildQueryString } from "@macrostrat/ui-components/lib/types";
import EditSample from "../components/edit-sample";

/** Info that propagates the right column when a left column button is clicked */

function SampleInfo({ data }) {
  console.log(data);

  const infoCard = () => {
    if (Object.keys(data).length > 1) {
      let lng = "null";
      let lat = "null";
      if (data.geometry !== null) {
        lng = data.geometry.coordinates[0];
        lat = data.geometry.coordinates[1];
      }

      return h("h4", [
        h("b", ["Longitude: "]),
        h("i", [lng]),
        h("b", [", "]),
        h("b", ["Latitude: "]),
        h("i", [lat]),
        h(Divider),
        h("h1", [data.name]),
        h(Divider),
        h("div", [h("h3", [h("b", ["Material: "]), h("i", [data.material])])]),
        h(Divider),
        h(EditSample),
      ]);
    } else {
      return h("h4", ["Click on a Sample"]);
    }
  };

  return h(Card, [h(infoCard)]);
}

export default SampleInfo;
