import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import h from "@macrostrat/hyper";
import { NavButton } from "~/components";
import { Card } from "@blueprintjs/core";

export function APIExplorerV2(props) {
  return h(Card, { className: "api-explorer-v2 bp4-light" }, [
    h("div.minimal-navbar", [
      h(
        NavButton,
        {
          className: "bp4-light",
          to: "/api-explorer/v1",
          minimal: false,
          large: true,
        },
        "Version 1"
      ),
      h(
        NavButton,
        {
          className: "bp4-light",
          to: "/import-schema-explorer",
          minimal: false,
          large: true,
        },
        "Import schemas"
      ),
    ]),
    h(SwaggerUI, { url: "/api/v2/schema" }),
  ]);
}
