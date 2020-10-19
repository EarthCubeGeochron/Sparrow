import * as React from "react";
import h from "@macrostrat/hyper";
import { useRouteMatch } from "react-router-dom";
import { useModelURL } from "~/util/router";
import { useAPIResult } from "@macrostrat/ui-components";
import { SampleListCard } from "../sample/list";
import styles from "./module.styl";
import { DownloadButton } from "../session";
import { Button, Divider, Spinner } from "@blueprintjs/core";
import { parse, format } from "date-fns";
import { LinkCard } from "@macrostrat/ui-components";
import { SampleCard } from "../sample/detail-card";
import { useAPIv2Result } from "~/api-v2";

/**
 * http://localhost:5002/api/v2/models/data_file?nest=data_file_link,sample,session
 * Things to display on the data-files page
 *  Date of Upload to Sparrow
 *  Basename
 *  type
 *  Sample Link Cards,
 *  Project Link Cards,
 *  Session Link Cards,
 */

const DetailPageHeader = (props) => {
  const { date_upload, basename, type: file_type, file_hash } = props;
  return h(
    "div",
    {
      style: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "baseline",
      },
    },
    [
      h("h2", [basename]),
      h("h4", ["Uploaded " + format(date_upload, "MMMM D, YYYY")]),
      h("div", [h(DownloadButton, { file_type, file_hash })]),
    ]
  );
};

/**
 *
 * @param props target, session_date, technique
 */
export const SessionCardInfo = (props) => {
  const { session_id, target, date, technique } = props;
  console.log(date);
  return h(
    "div",
    {
      style: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
        alignItems: "baseline",
      },
    },
    [
      h(
        "h5",
        { style: { color: "#1CBAFF", fontStyle: "italic", padding: "0px" } },
        ["Session Date: " + format(date, "MMMM D, YYYY")]
      ),
      h("h4", [technique]),
      h("h4", { style: { fontStyle: "italic" } }, ["Target: " + target]),
    ]
  );
};

export const SessionLinkCard = function(props) {
  const { session_id } = props;

  const to = useModelURL(`/session/${session_id}`);

  return h(
    LinkCard,
    {
      to,
      key: session_id,
      style: { marginBottom: "10px", maxHeight: "200px" },
    },
    h(SessionCardInfo, props)
  );
};

export const Samples = (props) => {
  const { name, sample_id, sample_material } = props;
  //let content = [h("p", "No samples")];
  if (props != null) {
    h(SampleCard, {
      name,
      id: sample_id,
      material: sample_material,
      link: true,
    });
  }
  return h("div.sample-area", [
    h("h4", "Samples"),
    h(
      "div",
      { style: { display: "flex", flexFlow: "row wrap", margin: "0 -5px" } },
      h(SampleCard, {
        name,
        id: sample_id,
        material: sample_material,
        link: true,
      })
    ),
  ]);
};

/**
 *
 * @param props session_id, technique, target, session_date, analysis
 */
export const SessionInfo = (props) => {
  const {
    session_id,
    technique,
    target,
    date,
    //analysis,
  } = props;
  //const analysisList = analysis.length > 1 ? " Analyses" : "Analysis";
  return h("div", { className: styles.sessionContainer }, [
    h("h4", ["Session "]),
    h(SessionLinkCard, { session_id, target, technique, date }),
  ]);
};

const ProjectLinks = (props) => {
  const { project } = props;
  if (project !== null) {
    const projectTo = useModelURL(`/project/${project.id}`);

    return h("div.project", [
      h("h4.info", "Project"),
      h("div", null, [h("a", { href: projectTo }, project.name) || "—"]),
    ]);
  }
  if (project == null) {
    return null;
  }
};

export function DataFilePage({ props }) {
  const { data } = props;
  console.log(data);
  if (!data) return h(Spinner);
  const {
    file_hash,
    type,
    data_file_link: [
      {
        date: date_upload,
        session: {
          date,
          technique,
          target,
          date_precision,
          analysis,
          id: session_id,
          sample: { name, id: sample_id, material: sample_material },
          project,
        },
      },
    ],
    basename,
  } = data;
  console.log(project);
  return h("div", { className: styles.data_page_container }, [
    h("div", { className: styles.header }, [
      h(DetailPageHeader, { date_upload, basename, type, file_hash }),
    ]),
    h(Divider),
    h("div", { className: styles.infoContainer }, [
      h("div", { className: styles.projects }, [h(ProjectLinks, { project })]),
      h("div", { className: styles.sampleContainer }, [
        h(Samples, { name, sample_id, sample_material }),
      ]),
      h(SessionInfo, {
        session_id,
        target,
        date,
        technique,
        analysis,
      }),
    ]),
  ]);
}

const DataFileComponent = function(props) {
  const { file_hash } = props;
  const dataFileURL = `/models/data_file/${file_hash}`;

  const initdata = useAPIv2Result(dataFileURL, {
    nest: "data_file_link,session,sample,project",
  });
  if (file_hash == null || initdata == null) {
    return null;
  }

  return h("div.data-view.project", [h(DataFilePage, { props: initdata })]);
};

export function DataFileMatch() {
  const {
    params: { file_hash },
  } = useRouteMatch();
  return h(DataFileComponent, { file_hash });
}
