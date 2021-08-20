import { hyperStyled } from "@macrostrat/hyper";
import { useRef, useMemo, useEffect, useState } from "react";
import {
  useAPIHelpers,
  CollapseCard,
  useElementSize,
} from "@macrostrat/ui-components";
import { APIV2Context, useAPIv2Result } from "~/api-v2";
import useWebSocket, { ReadyState } from "react-use-websocket";
import useResizeObserver from "use-resize-observer";
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
import { parse } from "ansicolor";
import classNames from "classnames";
import Form from "@rjsf/core";

const Row = ({ data, index, style }) => {
  const lineno = index - 1;
  const txt = data[lineno] ?? "";
  const spans = parse(txt).spans;

  return h(
    "div.message",
    {
      style: style,
    },
    [
      h.if(lineno >= 0 && lineno < data.length)(
        "span.lineno.dark-gray",
        `${lineno + 1}`
      ),
      h(
        "span.message-text",
        spans.map((d) => {
          const { italic, bold, text, color, bgColor } = d;
          const bg = bgColor?.name != null ? `bg-${bgColor.name}` : null;
          const className = classNames(
            {
              italic,
              bold,
              dim: color?.dim,
              "bg-dim": bgColor?.dim,
            },
            color?.name,
            bg
          );
          return h("span", { className }, text);
        })
      ),
    ]
  );
};

const LogWindow = ({ messages }) => {
  const ref = useRef<List>();
  const {
    ref: containerRef,
    width = 1,
    height = 1,
  } = useResizeObserver<HTMLDivElement>();
  const extraLines = 2;
  useEffect(() => {
    ref.current?.scrollToItem(messages.length + extraLines);
  }, [messages.length]);

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

function getDefaultsForSchema(schema) {
  let defaults = {};
  for (const key of Object.keys(schema)) {
    defaults[key] = schema[key].default;
  }
  return defaults;
}

function TaskMain({ tasks }) {
  const task = useParams().task;
  console.log(tasks, task);
  if (task == null) return null;
  console.log(tasks);
  const schema = tasks.find((d) => d.name == task).params;
  console.log(schema);
  const baseParams = getDefaultsForSchema(schema);
  const [params, setParams] = useState(baseParams);

  const helpers = useAPIHelpers(APIV2Context);
  //const url = helpers.buildURL("/import-tracker");
  const url = `ws://localhost:5002/api/v2/tasks/${task}`;

  const { sendMessage, lastMessage, readyState } = useWebSocket(url, {
    shouldReconnect: (closeEvent) => true,
  });
  const messageHistory = useRef([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showParameters, setShowParameters] = useState(false);

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
    h("div.task-control-ui", [
      h(MinimalNavbar, { className: "navbar" }, [
        h("h3", task),
        h(ButtonGroup, { minimal: true }, [
          h(
            Button,
            {
              rightIcon: isRunning ? "stop" : "play",
              disabled: readyState != ReadyState.OPEN,
              onClick() {
                let act = { action: isRunning ? "stop" : "start" };
                if (act.action == "start") act.params = params;
                sendMessage(JSON.stringify(act));
              },
            },
            isRunning ? "Stop" : "Start"
          ),
          h(
            Button,
            {
              onClick() {
                setShowParameters(!showParameters);
              },
            },
            `${showParameters ? "Hide" : "Show"} parameters`
          ),
        ]),
        h("div.status", "WebSocket connection: " + connectionStatus),
      ]),
      h(
        CollapseCard,
        { isOpen: showParameters },
        h(
          Form,
          {
            schema,
            className: "params-form",
            formData: params,
            liveValidate: true,
            omitExtraData: true,
            liveOmit: true,
            onChange(e) {
              setParams(e.formData);
            },
          },
          h("div")
        )
      ),
    ]),
    h(LogWindow, { messages: messageHistory.current }),
  ]);
}

const TasksRouter = ({ base, tasks }) => {
  return h(Switch, [
    h(Route, {
      path: base + "/:task",
      render: () => h(TaskMain, { tasks }),
    }),
    h(Route, {
      path: base,
      render: () =>
        h(NonIdealState, { title: "No task selected", icon: "applications" }),
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
  const res: { enabled: boolean; tasks: any[] } = useAPIv2Result("/tasks/")
    ?.data ?? { enabled: false, tasks: [] };
  const task = useParams().task ?? null;

  if (!res.enabled) {
    return h(
      "div.tasks-page",
      null,
      h(NonIdealState, {
        title: "Tasks disabled",
        description:
          "A tasks worker is not available for this Sparrow instance. Use the Sparrow command-line application to run tasks.",
        icon: "console",
      })
    );
  }

  const tasks = res.tasks;
  const base = "/admin/tasks";
  return h("div.tasks-page", [
    h("div.left-column", null, h(TaskList, { tasks, base, task })),
    h(TasksRouter, { base, tasks }),
  ]);
}

export default TasksPage;
