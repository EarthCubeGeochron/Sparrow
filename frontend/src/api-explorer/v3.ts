import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import h from "@macrostrat/hyper";
import { Card } from "@blueprintjs/core";
import { apiV3BaseURL } from "~/api/postgrest";

export function APIExplorerV3() {
  // PostgREST describes the data API at its root
  return h(Card, { className: "api-explorer-v3 bp4-light" }, [
    h(SwaggerUI, { url: apiV3BaseURL + "/" }),
  ]);
}
