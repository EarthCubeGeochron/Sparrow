import h from "@macrostrat/hyper";
import { useRef, useMemo, useEffect } from "react";
import { useAPIHelpers } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import useWebSocket, { ReadyState } from "react-use-websocket";

function ImporterMain() {
  const helpers = useAPIHelpers(APIV2Context);
  const url1 = helpers.buildURL("/import-tracker");
  const url = "ws://localhost:5002/api/v2/import-tracker";
  console.log(url);

  const { sendMessage, lastMessage, readyState } = useWebSocket(url, {
    onOpen: () => console.log("opened"),
  });
  const messageHistory = useRef([]);

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  messageHistory.current = useMemo(
    () => messageHistory.current.concat(lastMessage),
    [lastMessage]
  );

  useEffect(() => sendMessage("Hello"), []);

  return h("div", [
    h("div.status", "WebSocket connection: " + connectionStatus),
    h(
      "div.message-history",
      messageHistory.current.map((d) => `${d}`)
    ),
  ]);
}

function ImporterPage() {
  return h("div.importer-page", [h("div.left-column"), h(ImporterMain)]);
}

export default ImporterPage;
