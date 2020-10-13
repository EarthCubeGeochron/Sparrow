import * as React from "react";
import h from "@macrostrat/hyper";
import { useRouteMatch } from "react-router-dom";
import { useModelURL } from "~/util/router";
import { useAPIResult } from "@macrostrat/ui-components";
import { SampleListCard } from "../sample/list";
import styles from "./module.styl";
import { DownloadButton } from "../session";
import { Button, Spinner } from "@blueprintjs/core";
import { parse, format } from "date-fns";
import { LinkCard } from "@macrostrat/ui-components";
import { SampleCard } from "../sample/detail-card";

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
      },
    },
    [
      h("h2", [basename]),
      h("h4", [format(date_upload, "MMMM D, YYYY")]),
      h("div", [h(DownloadButton, { file_type, file_hash })]),
    ]
  );
};

/**
 *
 * @param props target, session_date, technique
 */
export const SessionCardInfo = (props) => {
  const { session_id, target, session_date, technique } = props;
  console.log(session_date);
  return h(
    "div",
    {
      style: {
        display: "flex",
        flexDirection: "row",
        justifyContent: "space-between",
      },
    },
    [
      h(
        "h5",
        { style: { color: "red", fontStyle: "italic", padding: "0px" } },
        [format(session_date, "MMMM D, YYYY")]
      ),
      h("h4", [technique]),
      h("h4", { style: { fontStyle: "italic" } }, [target]),
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
  const { sample_name, sample_id, sample_material } = props;
  //let content = [h("p", "No samples")];
  if (props != null) {
    h(SampleCard, {
      name: sample_name,
      id: sample_id,
      material: sample_material,
      link: true,
    });
  }
  return h("div.sample-area", [
    h("h4", "Samples:"),
    h(
      "div",
      { style: { display: "flex", flexFlow: "row wrap", margin: "0 -5px" } },
      h(SampleCard, {
        name: sample_name,
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
    session_date,
    //analysis,
  } = props;
  //const analysisList = analysis.length > 1 ? " Analyses" : "Analysis";
  return h("div", { className: styles.sessionContainer }, [
    // h("h3", ["Session: " + analysis.length + " " + analysisList]),
    h(SessionLinkCard, { session_id, target, technique, session_date }),
  ]);
};

const ProjectLinks = (props) => {
  const { project } = props;
  if (project !== null) {
    const projectTo = useModelURL(`/project/${project.id}`);

    return h("div.project", [
      h("h5.info", "Project"),
      h("div", null, [h("a", { href: projectTo }, project.name) || "—"]),
    ]);
  }
  if (project == null) {
    return h("div.project", [
      h("h5.info", "Project: "),
      h("div", { style: { fontStyle: "italic" } }, ["No project associated"]),
    ]);
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
          date: session_date,
          technique,
          target,
          date_precision,
          analysis,
          id: session_id,
          sample: {
            name: sample_name,
            id: sample_id,
            material: sample_material,
          },
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
    h("div", { className: styles.infoContainer }, [
      h(SessionInfo, {
        session_id,
        target,
        session_date,
        technique,
        analysis,
      }),
      h("div", { className: styles.sampleContainer }, [
        h(Samples, { sample_name, sample_id, sample_material }),
      ]),
      h("div", { className: styles.projects }, [h(ProjectLinks, { project })]),
    ]),
  ]);
}

//localhost:5002/api/v2/models/data_file/ff1bfe14-f808-761c-ad87-693bf6edaeb8?nest=data_file_link,session,sample,project

const DataFileComponent = function(props) {
  const { file_hash } = props;
  const dataFileURL = `http://localhost:5002/api/v2/models/data_file/${file_hash}`;

  const initdata = useAPIResult(dataFileURL, {
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
