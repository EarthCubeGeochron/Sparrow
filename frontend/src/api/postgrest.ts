/**
 * Sparrow's data API: PostgREST over the `sparrow_api` schema, at /api/v3.
 * Responses are flat arrays; nesting comes from `select=` embedding or from
 * separate requests combined on the client.
 */
import h from "@macrostrat/hyper";
import {
  APIContext,
  createAPIContext,
  useAPIActions,
  useAxiosInstance,
} from "@macrostrat/ui-components";
import { useContext, useEffect, useState } from "react";
import { Intent } from "@blueprintjs/core";
import join from "url-join";
import { AppToaster } from "~/toaster";
import { apiBaseURL } from "~/env";
import { useAuth } from "~/auth/context";

export const apiV3BaseURL = join(apiBaseURL, "/api/v3");

export const APIV3Context = createAPIContext({ baseURL: apiV3BaseURL });

/** PostgREST caps responses at this many rows (PGRST_DB_MAX_ROWS) */
export const maxRows = 100;

export type QueryParams = Record<string, string | number | boolean | null>;

let currentToken: string | null = null;
let interceptorAttached = false;

function isAbsolute(url: string | undefined) {
  return /^[a-z][a-z0-9+.-]*:\/\//i.test(url ?? "");
}

function attachToken(axiosInstance) {
  // Only relative routes reach our gateway; never send the token to other hosts
  axiosInstance.interceptors.request.use((cfg) => {
    if (currentToken != null && !isAbsolute(cfg.url)) {
      cfg.headers = { ...cfg.headers, Authorization: `Bearer ${currentToken}` };
    }
    return cfg;
  });
}

export function PostgRESTProvider({ children, onError }) {
  const { token } = useAuth();
  currentToken = token;
  // Above its own provider, this reads the context's default value
  const base = useContext(APIV3Context);
  if (!interceptorAttached) {
    attachToken(base.axiosInstance);
    interceptorAttached = true;
  }
  const value = { ...base, config: { ...base.config, onError } };
  // The default context also points here, for paged lists and lab plugins
  return h(
    APIV3Context.Provider,
    { value },
    h(APIContext.Provider, { value }, children)
  );
}

function cleanParams(params: QueryParams): QueryParams {
  const res = {};
  for (const [k, v] of Object.entries(params ?? {})) {
    if (v != null) res[k] = v;
  }
  return res;
}

export function usePostgRESTGet() {
  /** A GET bound to the signed-in user's token; resolves null on error */
  const { get } = useAPIActions(APIV3Context);
  return async function (route: string, params: QueryParams = {}) {
    return (await get(route, cleanParams(params), {})) ?? null;
  };
}

export async function getAllRows(get, route: string, params: QueryParams) {
  /** Page through a route that may return more than `maxRows` rows */
  let rows = [];
  for (let offset = 0; offset < 50 * maxRows; offset += maxRows) {
    const page = await get(route, { ...params, limit: maxRows, offset });
    if (page == null) return rows.length > 0 ? rows : null;
    rows = rows.concat(page);
    if (page.length < maxRows) break;
  }
  return rows;
}

interface ResultOptions<T> {
  unwrap?: (data: any) => T;
  /** Follow pagination past PostgREST's row cap */
  all?: boolean;
}

export function usePostgRESTResult<T = any>(
  route: string | null,
  params: QueryParams = {},
  opts: ResultOptions<T> = {}
): T | null {
  const { token } = useAuth();
  const get = usePostgRESTGet();
  const [result, setResult] = useState<T | null>(null);
  const paramKey = JSON.stringify(params);

  useEffect(() => {
    let current = true;
    // Never show one record's data while another's is loading
    setResult(null);
    if (route == null) return;
    const req = opts.all ? getAllRows(get, route, params) : get(route, params);
    req.then((data) => {
      if (!current) return;
      if (data != null && opts.unwrap != null) data = opts.unwrap(data);
      setResult(data);
    });
    return () => {
      current = false;
    };
  }, [route, paramKey, token]);

  return result;
}

export function useQueryResult<T>(
  query: ((get) => Promise<T | null>) | null,
  deps: any[]
): T | null {
  /** Run an async function of several requests, re-running when the user changes */
  const { token } = useAuth();
  const get = usePostgRESTGet();
  const [result, setResult] = useState<T | null>(null);

  useEffect(() => {
    let current = true;
    setResult(null);
    if (query == null) return;
    query(get).then((data) => {
      if (current) setResult(data);
    });
    return () => {
      current = false;
    };
  }, [...deps, token]);

  return result;
}

function showWriteError(err) {
  const detail = err?.response?.data?.message ?? err?.message ?? String(err);
  AppToaster.show({
    message: h("div.api-error", [
      h("p", "Changes were not saved"),
      h("p", detail),
    ]),
    intent: Intent.DANGER,
  });
}

async function reportErrors<T>(request: Promise<T>): Promise<T> {
  try {
    return await request;
  } catch (err) {
    showWriteError(err);
    throw err;
  }
}

export function usePostgRESTActions() {
  /** Writes; PostgREST only accepts them from the admin role */
  const axios = useAxiosInstance(APIV3Context);
  const prefer = { Prefer: "return=representation" };
  return {
    async insert(route: string, body: object | object[]) {
      const req = axios.post(route, body, { headers: prefer });
      return (await reportErrors(req)).data;
    },
    async update(route: string, filters: QueryParams, body: object) {
      const req = axios.patch(route, body, {
        params: filters,
        headers: prefer,
      });
      return (await reportErrors(req)).data;
    },
    async remove(route: string, filters: QueryParams) {
      await reportErrors(axios.delete(route, { params: filters }));
    },
  };
}

/** Quote a value for PostgREST's `and=`/`or=` logic trees */
export function quote(value: string | number): string {
  const s = String(value).replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  return `"${s}"`;
}

export function inList(values: (string | number)[]): string {
  return `in.(${values.map(quote).join(",")})`;
}
