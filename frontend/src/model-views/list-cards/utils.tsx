import { ModelCard } from "../utils";
import { useContext } from "react";
import hyper from "@macrostrat/hyper";
import { ContentArea, pluralize } from "../project/index";
import { parse, format } from "date-fns";
import styles from "./card.styl";

const h = hyper.styled(styles);

export const sampleContent = (props) => {
  const { material, id, name, location, session } = props;
  const Location =
    location != null
      ? h("div", [
          "[",
          location.coordinates[0].toFixed(3),
          ", ",
          location.coordinates[1].toFixed(3),
          "]",
        ])
      : h("div", "No Location");

  const sampleName = h("div", { style: { marginBottom: "5px" } }, [
    "Sample: ",
    h("span", name),
  ]);

  const Material =
    material != null
      ? h("div", { style: { marginBottom: "5px" } }, ["Material: ", material])
      : h("div", { style: { marginBottom: "5px" } }, "No material");

  const sessionDate = session.length > 0 ? session[0].date.split("T")[0] : null;

  return h("div.sample-content", [
    h("div.card-header", [h("div", id), Location]),
    h("div.bod", [sampleName, Material, sessionDate]),
  ]);
};

const SampleModelCard = (props) => {
  const {
    material,
    id,
    name,
    location,
    session,
    link = true,
    onClick = null,
  } = props;

  const content = h(sampleContent, { material, id, name, location, session });
  if (onClick == null) {
    return h(ModelCard, { id, content, model: "sample", link });
  }

  return h(ModelCard, {
    id,
    content,
    model: "sample",
    link,
    onClick: () => onClick(id, name),
  });
};

const PublicationModelCard = (props) => {
  const { year, id, title, doi, author, journal, onClick, link } = props;

  return h(ModelCard, {
    id,
    content: h("div", [title]),
    model: "publication",
    link,
    onClick: () => onClick(id, title, doi),
  });
};

export const ResearcherModelCard = (props) => {
  const { id, name, onClick, link } = props;

  return h(ModelCard, {
    id,
    content: h("div", [name]),
    model: "researcher",
    link,
    onClick: () => onClick(id, name),
  });
};

const ProjectModelCard = (props) => {
  const {
    id,
    name,
    description,
    samples = [],
    publication = [],
    link,
    onClick,
    minimal = false,
  } = props;

  const pubData =
    publication.length > 0
      ? publication.length > 1
        ? publication[0].title + "...."
        : publication[0].title
      : null;

  const content = h("div.project-card", [
    h("h3", name),
    h("p.description", description),
    samples.length > 0
      ? h(ContentOverFlow, {
          className: "samples",
          data: samples.map((d) => d.name),
          title: "sample",
        })
      : null,
    h.if(publication.length > 0)("div.content-area", [
      h("h5", [
        h("span.count", [
          publication.length + " " + pluralize("Publication", publication),
        ]),
        h("h5", [pubData]),
      ]),
    ]),
  ]);

  return h(ModelCard, {
    id,
    content,
    model: "project",
    link,
    onClick: () => onClick(id, name),
  });
};

const SessionModelCard = (props) => {
  const {
    session_id,
    target,
    date,
    technique,
    instrument,
    analysis,
    sample,
    data,
    link,
    onClick,
    onHover = false,
  } = props;

  const instruName = instrument ? instrument.name : "";
  const sampleName = sample ? sample.name : "";

  const Irradiation = data.Irradiation ? data.Irradiation : null;
  const FCS = data.FCS ? data.FCS : null;

  const analysisName = analysis.length > 1 ? "Analyses" : "Analysis";
  const analysisCount = analysis.length + " " + analysisName;

  const classname = onHover ? "session-card-hover" : "session-card";

  const content = h(`div.${classname}`, [
    h("div.card-header", [
      h("div", [format(date, "MMMM D, YYYY")]),
      sampleName,
    ]),
    h("div.bod", [
      h.if(FCS)("div", [FCS]),
      h("div", [h("span", technique)]),
      h("div", ["Instrument: " + instruName]),
      h.if(Irradiation)("div", [Irradiation]),
    ]),
    h("div.footer", [h("div", analysisCount), h("div", ["Target: " + target])]),
  ]);

  return h(ModelCard, {
    id: session_id,
    content,
    model: "session",
    link,
    onClick: () => onClick(session_id, date, target, technique),
  });
};

const DataFileModelCard = (props) => {
  const { file_hash, basename, type, date, data_file_link: link } = props;

  let sampleName = "";
  if (link.length > 0) {
    if (link[0].session) {
      sampleName += link[0].session.sample.name;
    }
  }

  const content = h("div.session-card", [
    h("div.card-header", [
      h("div", [format(date, "MMMM D, YYYY")]),
      sampleName,
    ]),
    h("div.bod", [h("div", [h("span", basename)]), h("div", [type])]),
  ]);

  return h(ModelCard, { id: file_hash, content, model: "data-file" });
};

const ContentOverFlow = ({ data, title, className, minimal = false }) =>
  h("div.content-area", { style: { margin: "0px" } }, [
    h("h5", [h("span.count", data.length), " ", pluralize(title, data)]),
    h.if(!minimal)(
      "ul",
      { className },
      data.length > 2
        ? h("div", [data.slice(0, 2).map((d) => h("li", d)), "More..."])
        : data.map((d) => h("li", d))
    ),
  ]);

export {
  SampleModelCard,
  ProjectModelCard,
  SessionModelCard,
  DataFileModelCard,
  PublicationModelCard,
};
