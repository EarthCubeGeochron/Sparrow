import { hyperStyled } from "@macrostrat/hyper";
import { useRef, useMemo, useEffect, useState } from "react";
import { ControlledSlider, useAPIHelpers } from "@macrostrat/ui-components";
import { APIV2Context, useAPIv2Result } from "~/api-v2";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { MinimalNavbar } from "~/components";
import {
  Button,
  ButtonGroup,
  Menu,
  MenuItem,
  NonIdealState,
} from "@blueprintjs/core";
import styles from "./module.styl";
import { FixedSizeList as List } from "react-window";
const h = hyperStyled(styles);
import { useParams, Switch, Route } from "react-router";
import { Link } from "react-router-dom";
import { useElementSize } from "@earthdata/sheet/src";

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
  const containerRef = useRef<HTMLElement>();
  const extraLines = 2;
  useEffect(() => {
    ref.current?.scrollToItem(messages.length + extraLines - 1);
  }, [messages.length]);

  const { width, height } = useElementSize(containerRef, true) ?? {
    width: 0,
    height: 0,
  };

  return h(
    "div.log-window",
    { ref: containerRef },
    h(
      List,
      {
        ref,
        height,
        itemCount: messages.length + extraLines,
        itemSize: 18,
        itemData: messages,
        width,
        className: "message-history",
      },
      Row
    )
  );
};

const statusOptions = {
  [ReadyState.CONNECTING]: "Connecting",
  [ReadyState.OPEN]: "Open",
  [ReadyState.CLOSING]: "Closing",
  [ReadyState.CLOSED]: "Closed",
  [ReadyState.UNINSTANTIATED]: "Uninstantiated",
};

function TaskMain({ task }) {
  task = useParams().task;
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

  return h("div.tasks-main", [
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

const TasksRouter = ({ base }) => {
  return h(Switch, [
    h(Route, {
      path: base + "/:task",
      render: () => h(TaskMain),
    }),
    h(Route, {
      path: base,
      render: () =>
        h(NonIdealState, { message: "No task selected", icon: "warning" }),
      exact: true,
    }),
  ]);
};

function TaskList({ tasks, base, task }) {
  return h("div.tasks-list", [
    h("h3", "Tasks"),
    h(
      Menu,
      (tasks ?? []).map((d) =>
        h(MenuItem, {
          text: h(Link, { to: base + `/${d.name}` }, d.name),
          selected: d.name === task,
          disabled: d.name === task,
        })
      )
    ),
  ]);
}

function TasksPage() {
  const tasks: any[] = useAPIv2Result("/tasks/")?.data ?? [];
  const task = useParams().task ?? null;
  const base = "/admin/tasks";
  return h("div.tasks-page", [
    h("div.left-column", null, h(TaskList, { tasks, base, task })),
    h(TasksRouter, { base }),
  ]);
}

export default TasksPage;
