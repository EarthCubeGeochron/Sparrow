import { Button, IconName, Intent } from "@blueprintjs/core";
import h from "@macrostrat/hyper";
import { APIV2Context } from "~/api-v2";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { useState, useCallback, useContext } from "react";

function ServerStatus(props) {
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
      uri = uri.replace(/^http(s)?:\/\//, "ws$1://") + "/heartbeat";
      console.log(uri);
      resolve(uri);
    });
  }, [ctx, reconnectAttempt]);

  const { sendMessage, lastMessage, readyState } = useWebSocket(getSocketUrl, {
    onOpen: () => setConnected(true),
    shouldReconnect: (closeEvent) => {
      return true;
    },
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  let icon: IconName = "tick";
  let intent: Intent = "success";
  let text: string = "Connected";
  if (!hasEverConnected) {
    icon = "error";
    intent = "danger";
    text = "Server not found";
  } else if (readyState != ReadyState.OPEN) {
    icon = "warning-sign";
    intent = "warning";
    text = "Server disconnected";
  }

  return h(
    Button,
    {
      minimal: true,
      small: true,
      icon,
      intent,
      onClick() {
        if (readyState != ReadyState.OPEN)
          setReconnectAttempt(reconnectAttempt + 1);
      },
    },
    text
  );
}

export { ServerStatus };
