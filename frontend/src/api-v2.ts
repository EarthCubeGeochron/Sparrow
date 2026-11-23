import {
  createAPIContext,
  useAPIResult,
  APIOptions,
} from "@macrostrat/ui-components";
import join from "url-join";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { useCallback, useContext, useState } from "react";
import { apiBaseURL } from "./env";

export const APIV2Context = createAPIContext({
  baseURL: join(apiBaseURL, "/api/v2"),
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

export const APIV3Context = createAPIContext({
  baseURL: join(apiBaseURL, "/api/v3"),
});

export function useAPIv3Result(
  route,
  params = {},
  opts: Partial<APIOptions> = {}
) {
  /** Temporary shim to convert V1 API to V2 */
  opts.context = APIV3Context;
  return useAPIResult(route, params, opts);
}

export function useSparrowWebSocket(path: string, options = {}) {
  /** An expanded function to use a websocket */
  const [reconnectAttempt, setReconnectAttempt] = useState(1);
  const [hasEverConnected, setConnected] = useState(false);
  const ctx = useContext(APIV2Context);
  const getSocketUrl = useCallback(() => {
    return new Promise((resolve) => {
      let uri = ctx.baseURL;
      // Get absolute and websocket URL
      if (!uri.startsWith("http")) {
        const { protocol, host } = window.location;
        uri = `${protocol}//${host}${uri}`;
      }
      uri = uri.replace(/^http(s)?:\/\//, "ws$1://") + path;
      resolve(uri);
    });
  }, [ctx, path, reconnectAttempt]);

  const socket = useWebSocket(getSocketUrl, {
    onOpen() {
      setConnected(true);
    },
    shouldReconnect() {
      return true;
    },
    ...options,
  });

  const isOpen = socket.readyState == ReadyState.OPEN;

  const tryToReconnect = useCallback(() => {
    if (!isOpen) setReconnectAttempt(reconnectAttempt + 1);
  }, [setReconnectAttempt, isOpen, reconnectAttempt]);

  return {
    ...socket,
    reconnectAttempt,
    hasEverConnected,
    tryToReconnect,
    isOpen,
  };
}
