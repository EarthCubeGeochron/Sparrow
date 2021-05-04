import * as React from "react";
import h from "@macrostrat/hyper";
import { AnchorButton, Intent } from "@blueprintjs/core";
import { Frame, useFrameOverride } from "~/frame";
import { EditableSessionDetails } from "./editor";
import { SessionDetailPanel } from "./detail-panel";
import { APIResultView } from "@macrostrat/ui-components";
import { useRouteMatch } from "react-router-dom";
import { Tab, Tabs } from "@blueprintjs/core";

/**
 *
 * @param props : file_hash, type: as file_type
 */
export function DownloadButton(props) {
  const { file_hash, file_type } = props;

  let text: any | React.ReactNode = "Data file";
  if (file_type != null) {
    text = h([h("b", file_type), " file"]);
  }

  const href = `${process.env.BASE_URL}api/v2/data_file/${file_hash}`;
  return h(
    AnchorButton,
    { href, icon: "document", intent: Intent.PRIMARY },
    text
  );
}

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
      id: "sessionDetailTabs",
    },
    [
      extraTabs.map(({ title, component, id }) =>
        h(Tab, { id, panel: h(component, props) }, title)
      ),
      h(
        Tab,
        { id: "analysisDetails", panel: coreComponent },
        "Analysis details"
      ),
    ]
  );
}

function SessionComponent(props) {
  let { id } = props;
  if (id == null) {
    return null;
  }

  return h("div.data-view#session", [
    h(
      APIResultView,
      {
        route: "/session",
        params: { id },
      },
      (data) => {
        let rest, sample_name;
        const res = data[0];
        ({ sample_name, id, ...rest } = res);
        return h("div", [
          h(EditableSessionDetails, { id }),
          //h(SessionInfoCard, res),
          h("div.data-files", [
            h("h3", "Data sources"),
            // h(Frame, { id: "dataFileDownloadButton", ...rest }, (props) => {
            //   return h(DownloadButton, props);
            // }),
          ]),
          h(
            Frame,
            {
              id: "sessionDetail",
              session_id: id,
            },
            SessionPageTabs
          ),
        ]);
      }
    ),
  ]);
}

function SessionMatch(props) {
  const {
    params: { id },
  } = useRouteMatch();
  return h(SessionComponent, { id });
}

export { SessionComponent, SessionMatch };
