import { hyperStyled } from "@macrostrat/hyper";
import { useRef, useMemo, useEffect, useState } from "react";
import { ControlledSlider, useAPIHelpers } from "@macrostrat/ui-components";
import { APIV2Context, useAPIv2Result } from "~/api-v2";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { MinimalNavbar } from "~/components";
import { Button, ButtonGroup, Menu, MenuItem } from "@blueprintjs/core";
import styles from "./module.styl";
import { FixedSizeList as List } from "react-window";
const h = hyperStyled(styles);

const Row = ({ data, index, style }) => {
  return h(
    "div.message",
    {
      style: style,
    },
    data[index]
  );
};

const LogWindow = ({ messages }) => {
  const ref = useRef<List>();
  useEffect(() => {
    ref.current?.scrollToItem(messages.length - 1);
  }, [messages.length]);
  return h(
    List,
    {
      ref,
      height: 600,
      itemCount: messages.length,
      itemSize: 18,
      itemData: messages,
      width: 1200,
      className: "message-history",
    },
    Row
  );
};

const statusOptions = {
  [ReadyState.CONNECTING]: "Connecting",
  [ReadyState.OPEN]: "Open",
  [ReadyState.CLOSING]: "Closing",
  [ReadyState.CLOSED]: "Closed",
  [ReadyState.UNINSTANTIATED]: "Uninstantiated",
};

function ImporterMain({ task }) {
  if (task == null) return null;

  const helpers = useAPIHelpers(APIV2Context);
  //const url = helpers.buildURL("/import-tracker");
  const url = `ws://localhost:5002/api/v2/tasks/${task}`;

  const { sendMessage, lastMessage, readyState } = useWebSocket(url, {
    shouldReconnect: (closeEvent) => true,
  });
  const messageHistory = useRef([]);
  const [isRunning, setIsRunning] = useState(false);

  const connectionStatus = statusOptions[readyState];

  messageHistory.current = useMemo(() => {
    let message = null;
    if (lastMessage?.data != null) {
      try {
        message = JSON.parse(lastMessage.data);
      } catch (error) {}
    }
    if (message?.action == "start") {
      setIsRunning(true);
      return [];
    } else if (message?.action == "stop") {
      setIsRunning(false);
    }
    const text = message?.text;
    if (text != null) {
      const lines = text.split("\n").filter((line) => line.length > 0);
      messageHistory.current?.push(...lines);
    }
    return messageHistory.current;
  }, [lastMessage]);

  return h("div.importer-main", [
    h(MinimalNavbar, { className: "navbar" }, [
      h("h3", task),
      h(ButtonGroup, { minimal: true }, [
        h(
          Button,
          {
            rightIcon: isRunning ? "stop" : "play",
            disabled: readyState != ReadyState.OPEN,
            onClick() {
              sendMessage(
                JSON.stringify({ action: isRunning ? "stop" : "start" })
              );
            },
          },
          isRunning ? "Stop" : "Start"
        ),
      ]),
      h("div.status", "WebSocket connection: " + connectionStatus),
    ]),
    h(LogWindow, { messages: messageHistory.current }),
  ]);
}

function TaskList({ tasks, selectedTask, onSelect }) {
  return h("div.pipelines-list", [
    h("h3", "Pipelines"),
    h(
      Menu,
      (tasks ?? []).map((d) =>
        h(MenuItem, {
          text: d.name,
          active: selectedTask == d,
          onClick() {
            onSelect(d);
          },
        })
      )
    ),
  ]);
}

function ImporterPage() {
  const tasks: any[] = useAPIv2Result("/tasks/")?.data ?? [];
  const [task, setTask] = useState(null);
  return h("div.importer-page", [
    h(
      "div.left-column",
      null,
      h(TaskList, { tasks, selectedTask: task, onSelect: setTask })
    ),
    h(ImporterMain, { task: task?.name }),
  ]);
}

export default ImporterPage;
