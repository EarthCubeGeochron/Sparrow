import { Button, IconName, Intent } from "@blueprintjs/core";
import h from "@macrostrat/hyper";
import { useSparrowWebSocket } from "~/api-v2";

function ServerStatus(props) {
  const {
    socket = useSparrowWebSocket("/heartbeat", {
      reconnectAttempts: 10,
      reconnectInterval: 3000,
    }),
    ...rest
  } = props;
  const { isOpen, tryToReconnect, hasEverConnected } = socket;

  let icon: IconName = "tick";
  let intent: Intent = "success";
  let text: string = "Connected";
  if (!hasEverConnected) {
    icon = "error";
    intent = "danger";
    text = "Server not found";
  } else if (!isOpen) {
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
        tryToReconnect();
      },
      ...rest,
    },
    text
  );
}

export { ServerStatus };
