/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "react-hyperscript";
import { Component } from "react";
import {
  Breadcrumbs,
  Button,
  AnchorButton,
  Intent,
  Tab,
  Tabs,
} from "@blueprintjs/core";
import { Link } from "react-router-dom";
import { Frame } from "app/frame";

import { SessionInfoCard } from "./info-card";
import { SessionDetailPanel } from "./detail-panel";
import { APIResultView } from "@macrostrat/ui-components";

class DownloadButton extends Component {
  render() {
    const { file_hash, file_type } = this.props;

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
}

class SessionComponent extends Component {
  render() {
    let { id } = this.props;
    if (id == null) {
      return null;
    }

    const breadCrumbs = [
      { text: h(Link, { to: "/catalog/session" }, "Sessions") },
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
}

export { SessionComponent };
