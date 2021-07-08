import * as React from "react";
import h from "@macrostrat/hyper";
import { AnchorButton, Intent } from "@blueprintjs/core";
import { Frame, useFrameOverride } from "~/frame";
import { EditableSessionDetails } from "./editor";
import { SessionDetailPanel } from "./detail-panel";
import { APIResultView, useAPIResult } from "@macrostrat/ui-components";
import { useRouteMatch } from "react-router-dom";
import { Tab, Tabs } from "@blueprintjs/core";

interface TabDef {
  id: string;
  title: string;
  component: React.ComponentType<any>;
}

function SessionPageTabs(props) {
  const coreComponent = h(SessionDetailPanel, { showTitle: true, ...props });
  const extraTabs: TabDef[] = useFrameOverride("sessionDetailTabs");
  if (extraTabs == null) {
    return coreComponent;
  }

  return h(
    Tabs,
    {
      id: "sessionDetailTabs"
    },
    [
      extraTabs.map(({ title, component, id }) =>
        h(Tab, { id, panel: h(component, props) }, title)
      ),
      h(
        Tab,
        { id: "analysisDetails", panel: coreComponent },
        "Analysis details"
      )
    ]
  );
}

function SessionComponent(props) {
  let { id } = props;
  if (id == null) {
    return null;
  }

  return h("div.data-view#session", [
    h(EditableSessionDetails, { id }),
    h("div.data-files", [
      h("h3", "Data sources")
      // h(Frame, { id: "dataFileDownloadButton", ...rest }, (props) => {
      //   return h(DownloadButton, props);
      // }),
    ]),
    h(
      Frame,
      {
        id: "sessionDetail",
        session_id: id
      },
      [SessionPageTabs]
    )
  ]);
}

function SessionMatch(props) {
  const {
    params: { id }
  } = useRouteMatch();
  return h(SessionComponent, { id });
}

export { SessionComponent, SessionMatch };
