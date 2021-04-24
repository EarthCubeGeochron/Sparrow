import h from "@macrostrat/hyper";
import { useRef, useMemo } from "react";
import { useAPIHelpers } from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import useWebSocket, { ReadyState } from "react-use-websocket";

function ImporterMain() {
  const helpers = useAPIHelpers(APIV2Context);
  const url1 = helpers.buildURL("/import-tracker");
  const url = "wss://localhost:5002/api/v2/import-tracker";
  console.log(url);

  const { sendMessage, lastMessage, readyState } = useWebSocket(url);
  const messageHistory = useRef([]);

  messageHistory.current = useMemo(
    () => messageHistory.current.concat(lastMessage),
    [lastMessage]
  );

  return h(
    "div",
    messageHistory.current.map((d) => `${d}`)
  );
}

function ImporterPage() {
  return h("div.importer-page", [h("div.left-column"), h(ImporterMain)]);
}

export default ImporterPage;
