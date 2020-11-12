import { hyperStyled } from "@macrostrat/hyper";
import { useParams } from "react-router-dom";
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

const h = hyperStyled(styles);

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

export const SessionLinkCard = function (props) {
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
  const { samples } = props;

  if (samples.length == 0) return h("p", "No samples");

  return h("div.sample-container", [
    h("h4", "Samples"),
    h(
      "div.samples",
      { style: { display: "flex", flexFlow: "row wrap", margin: "0 -5px" } },
      samples.map((d) => {
        const { name, sample_id, sample_material } = d;
        return h(SampleCard, {
          name,
          id: sample_id,
          material: sample_material,
          link: true,
        });
      })
    ),
  ]);
};

/**
 *
 * @param props sessions
 */
export const SessionInfo = (props) => {
  const { sessions } = props;
  //const analysisList = analysis.length > 1 ? " Analyses" : "Analysis";
  return h("div.session-container", [
    h("h4", null, "Sessions"),
    h(
      "div.sessions",
      sessions.map((d) => {
        const {
          id,
          technique,
          target,
          date,
          //analysis,
        } = d;
        return h(SessionLinkCard, { session_id: id, target, technique, date });
      })
    ),
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
    data_file_link, // is an array
    basename,
  } = data;

  // Get uploaded date from first link
  const { date } = data_file_link[0];

  const sessions = data_file_link
    .map((d) => d.session)
    .filter((d) => d != null);

  const samples = data_file_link.map((d) => d.sample).filter((d) => d != null);

  //console.log(project);
  return h("div.data-page-container", [
    h("div.header", [
      h(DetailPageHeader, { date_upload: date, basename, type, file_hash }),
    ]),
    h(Divider),
    h("div.info-container", [
      //h("div.projects", [h(ProjectLinks, { project })]),
      h(Samples, { samples }),
      h(SessionInfo, { sessions }),
    ]),
  ]);
}

const DataFileComponent = function (props) {
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
  const { file_hash } = useParams();
  return h(DataFileComponent, { file_hash });
}
