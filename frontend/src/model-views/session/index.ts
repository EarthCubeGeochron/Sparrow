/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import * as React from "react";
import h from "@macrostrat/hyper";
import { Breadcrumbs, AnchorButton, Intent } from "@blueprintjs/core";
import { Link } from "react-router-dom";
import { Frame } from "app/frame";

import { SessionInfoCard } from "./info-card";
import { SessionDetailPanel } from "./detail-panel";
import { APIResultView } from "@macrostrat/ui-components";
import { useModelURL } from "~/util/router";
import { useRouteMatch } from "react-router-dom";

/**
 *
 * @param props : file_hash, type: as file_type
 */
export function DownloadButton(props) {
  const { file_hash, file_type } = props;

  let text = "Data file";
  if (file_type != null) {
    text = h([h("b", file_type), " file"]);
  }

  const href = `${process.env.BASE_URL}data-file/${file_hash}`;
  return h(
    AnchorButton,
    { href, icon: "document", intent: Intent.PRIMARY },
    text
  );
}

function SessionComponent(props) {
  let { id } = props;
  if (id == null) {
    return null;
  }
  const to = useModelURL("/session");
  const breadCrumbs = [
    { text: h(Link, { to }, "Sessions") },
    { icon: "document", text: h("code.session-id", id) },
  ];

  return h("div.data-view#session", [
    h(Breadcrumbs, { items: breadCrumbs }),
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
          h(SessionInfoCard, res),
          h("div.data-files", [
            h("h3", "Data sources"),
            h(Frame, { id: "dataFileDownloadButton", ...rest }, (props) => {
              return h(DownloadButton, props);
            }),
          ]),
          h(Frame, { id: "sessionDetail", session_id: id }, (props) => {
            return h(SessionDetailPanel, { showTitle: true, ...props });
          }),
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
