import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import h from "@macrostrat/hyper";
import { useContext } from "react";
import { useAPIResult, APIContext } from "@macrostrat/ui-components";

export function APIExplorerV2(props) {
  return h(SwaggerUI, { url: "/api/v2/schema" });
}

export function useAPIv2Result(route, params, opts) {
  /** Temporary shim to convert V1 API to V2 */
  const { baseURL } = useContext(APIContext);
  const r1 = baseURL.replace("v1", "v2") + route;
  return useAPIResult(r1, params, opts);
}
