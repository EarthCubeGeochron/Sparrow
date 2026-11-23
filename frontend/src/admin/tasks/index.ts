import { hyperStyled } from "@macrostrat/hyper";
import { useRef, useMemo, useState, useEffect } from "react";
import { CollapseCard } from "@macrostrat/ui-components";
import { useAPIv2Result } from "~/api-v2";
import { MinimalNavbar, ServerStatus } from "~/components";
import { Button, Menu, MenuItem, NonIdealState } from "@blueprintjs/core";
import styles from "./module.styl";
const h = hyperStyled(styles);
import { useParams, Switch, Route } from "react-router";
import { Link, useHistory } from "react-router-dom";
import Form from "@rjsf/core";
import { useSparrowWebSocket } from "~/api-v2";
import { LogWindow } from "./log-window";

function getDefaultsForSchema(schema) {
  if (schema == null) return null;
  let defaults = {};
  for (const key of Object.keys(schema.properties)) {
    defaults[key] = schema[key]?.default;
  }
  return defaults;
}

function getChunkedMessages(msg) {
  if (msg?.data == null) return [];
  try {
    const data = JSON.parse(msg.data);
    // We have an array of messages
    if (Array.isArray(data)) return data;
    // We have a chunked message
    if (data.messages != null) return data.messages;
    // We have a single message
    return [data];
  } catch (error) {
    console.error(error);
  }
  return [];
}

function isStopMessage(message) {
  const { action, type, text } = message;
  return action == "stop" || (type == "control" && text == "Task finished");
}

function TaskMain({ tasks, task }) {
  if (task == null) return null;
  const schema = tasks.find((d) => d.name == task).params;
  const baseParams = getDefaultsForSchema(schema);
  const [params, setParams] = useState(baseParams);

  const ws = useSparrowWebSocket(`/tasks/${task}`);

  const { sendMessage, lastMessage, isOpen } = ws;
  const messageHistory = useRef([]);
  const [isRunning, setIsRunning] = useState(false);
  const [showParameters, setShowParameters] = useState(false);

  messageHistory.current = useMemo(() => {
    const chunkedMessages = getChunkedMessages(lastMessage);
    for (const message of chunkedMessages) {
      const { action, text, info, type } = message;
      if (action == "reset") {
        return [];
      } else if (action == "start") {
        setIsRunning(true);
      } else if (isStopMessage(message)) {
        setIsRunning(false);
      }
      if (info != null) {
        console.log(info);
      }
      // Actually track the message in hostory
      if (text != null) {
        // We could eventually keep track of line type here...
        const lines = text.split("\n").filter((line) => line.length > 0);
        messageHistory.current?.push(...lines);
      }
    }
    return messageHistory.current;
  }, [lastMessage]);

  return h("div.tasks-main", [
    h("div.task-control-ui", [
      h(MinimalNavbar, { className: "navbar" }, [
        h("h3", task),
        h(
          Button,
          {
            onClick() {
              setShowParameters(!showParameters);
            },
            active: showParameters,
            rightIcon: showParameters ? "chevron-up" : "chevron-down",
            minimal: true,
            disabled: schema == null,
          },
          `Parameters`
        ),
        h(
          Button,
          {
            rightIcon: isRunning ? "stop" : "play",
            disabled: !isOpen,
            minimal: true,
            onClick() {
              let act = { action: isRunning ? "stop" : "start" };
              if (act.action == "start") act.params = params ?? {};
              sendMessage(JSON.stringify(act));
            },
          },
          isRunning ? "Stop" : "Start"
        ),
        h("div.spacer", { style: { flexGrow: 1 } }),
        h(ServerStatus, { socket: ws, small: false }),
      ]),
      h.if(schema != null)(
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

const TaskRoute = ({ tasks }) => {
  const task = useParams().task;
  return h(TaskMain, { tasks, task, key: task });
};

const TasksRouter = ({ base, tasks }) => {
  return h(Switch, [
    h(Route, {
      path: base + "/:task",
      render: () => h(TaskRoute, { tasks }),
    }),
    h(Route, {
      path: base,
      render: () =>
        h(NonIdealState, { title: "No task selected", icon: "applications" }),
      exact: true,
    }),
  ]);
};

function TaskMenuItem({ taskName, base, isActive }) {
  const history = useHistory();

  const linkDest = base + `/${taskName}`;
  return h(MenuItem, {
    active: isActive,
    selected: isActive,
    text: h(
      Link,
      {
        to: linkDest,
      },
      taskName
    ),
    onClick(e) {
      history.push(linkDest);
      e.preventDefault();
    },
  });
}

function TaskList({ tasks = [], base, task }) {
  return h("div.tasks-list", [
    h("h3", "Tasks"),
    h(
      Menu,
      tasks.map((d) =>
        h(TaskMenuItem, { taskName: d.name, base, isActive: d.name === task })
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
