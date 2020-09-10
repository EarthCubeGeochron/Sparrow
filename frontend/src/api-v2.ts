import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import h from "@macrostrat/hyper";
import { useAPIHelpers } from "@macrostrat/ui-components";

export function APIExplorerV2(props) {
  return h(SwaggerUI, { url: "/api/v2/schema" });
}
