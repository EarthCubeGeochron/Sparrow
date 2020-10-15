import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";
import h from "@macrostrat/hyper";
import {
  createAPIContext,
  useAPIResult,
  APIOptions,
} from "@macrostrat/ui-components";
import { join } from "path";

export function APIExplorerV2(props) {
  return h(SwaggerUI, { url: "/api/v2/schema" });
}

const APIV2Context = createAPIContext({
  baseURL: join(process.env.BASE_URL ?? "/", "/api/v2"),
});

export function useAPIv2Result(
  route,
  params = {},
  opts: Partial<APIOptions> = {}
) {
  /** Temporary shim to convert V1 API to V2 */
  opts.context = APIV2Context;
  return useAPIResult(route, params, opts);
}

export { APIV2Context };
