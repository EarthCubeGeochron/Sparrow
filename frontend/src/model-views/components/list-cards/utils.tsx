import { useState, useEffect, ReactNode } from "react";
import { Frame } from "~/frame";
import { hyperStyled } from "@macrostrat/hyper";
import { Link } from "react-router-dom";
import { FormattedLngLat, pluralize } from "../new-model";
import { useModelURL } from "~/util";
import styles from "./card.styl";
import { PageViewDate, ProjectCardContent, Publication } from "~/model-views";

const h = hyperStyled(styles);

function clickedClassname(props) {
  const { clicked, id } = props;
  if (clicked == `${id}`) {
    return "model-card.clicked";
  } else {
    return "model-card";
  }
}

type ModelCardProps = {
  content: ReactNode;
  id: number;
  model: string;
  showIdentity?: "long" | "short" | null;
  link: boolean;
  onClick?: () => void;
};

export function ModelCard(props: ModelCardProps) {
  const {
    content,
    id,
    model,
    showIdentity = null,
    link = true,
    onClick = () => {},
  } = props;

  const [clicked, setClicked] = useState();

  useEffect(() => {
    const list = window.location.pathname.split("/");
    if (list.length > 3) {
      setClicked(list[3]); //list[3] will be the id
    }
  }, [window.location.pathname]);

  const to = useModelURL(`/${model}/${id}`);

  const classname = clickedClassname({ clicked, id });

  let idInfo = showIdentity == "long" ? `${model} ${id}` : id;

  if (link) {
    return h(Link, { to, style: { textDecoration: "none" } }, [
      h(`div.${classname}`, [
        h.if(showIdentity != null)("div.id-info", idInfo),
        content,
      ]),
    ]);
  } else {
    return h("div", [
      h(
        `div.${classname}`,
        {
          onClick,
        },
        [content]
      ),
    ]);
  }
}

function sessionDates({ session }) {
  if (session.length == 0) return [];

  const dates = session.map((ss) => {
    const date = ss.date.split("T")[0];
  });

  return dates;
}

function SampleDefaultContent(props) {
  const { material, id, name, location, session } = props;

  const sampleName = h("div", { style: { marginBottom: "5px" } }, [
    h("span", name),
  ]);

  const Material = h.if(material)("div", { style: { marginBottom: "5px" } }, [
    "Material: ",
    material,
  ]);

  const sessionDate = sessionDates({ session });

  return h("div.sample-content", [
    h("div.card-header", [
      h("div.bod", [sampleName]),
      h(FormattedLngLat, { location }),
    ]),
    h("div.bod", [
      Material,
      sessionDate.map((date) => {
        if (sessionDate.length > 0) {
          return h("div", date);
        }
      }),
    ]),
  ]);
}

const SampleModelCard = (props) => {
  const {
    material,
    id,
    name,
    location,
    session = [],
    link = true,
    showIdentity,
    onClick = null,
  } = props;

  const sample = { material, id, name, location, session };

  const content = h(
    Frame,
    {
      id: "sampleCardContent",
      data: { material, id, name, location, session },
    },
    h(SampleDefaultContent, { material, id, name, location, session })
  );
  if (onClick == null) {
    return h(ModelCard, { id, content, model: "sample", link, showIdentity });
  }

  return h(ModelCard, {
    id,
    content,
    showIdentity,
    model: "sample",
    link,
    onClick: () => onClick(sample),
  });
};

const interior = ({ doi, title }) => {
  let doiAddendum = [];
  if (doi != null) {
    doiAddendum = [
      " – ",
      h("span.doi-info", [
        h("span.label", "DOI:"),
        h("span.doi.bp3-monospace-text", doi),
      ]),
    ];
  }
  return h("div", { style: { margin: "10px" } }, [
    h("span.title", title),
    ...doiAddendum,
  ]);
};

const PublicationModelCard = (props) => {
  const { year, id, title, doi, author, journal, onClick, link, showIdentity } =
    props;

  const content = h(Frame, { id: "publicationCardContent" }, [
    h(interior, { title, doi }),
  ]);

  return h(ModelCard, {
    id,
    content,
    showIdentity,
    model: "publication",
    link,
    onClick: () => onClick(id, title, doi),
  });
};

export const ResearcherModelCard = (props) => {
  const { id, name, onClick, link, showIdentity } = props;

  const content = h(
    Frame,
    { id: "researcherCardContent", data: { id, name } },
    h("h4", { style: { margin: "10px" } }, name)
  );

  return h(ModelCard, {
    id,
    content,
    showIdentity,
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
    sample = [],
    session = [],
    publication = [],
    link,
    onClick,
    showIdentity,
    minimal = false,
  } = props;

  const content = h(ProjectCardContent, {
    name,
    description,
    sample,
    session,
    publication,
  });

  const cardContent = h(
    Frame,
    {
      id: "projectCardContent",
      data: { id, name, description, sample, session, publication },
    },
    content
  );

  return h(ModelCard, {
    id,
    showIdentity,
    content: cardContent,
    model: "project",
    link,
    onClick: () => onClick(id, name),
  });
};

const SessionListContent = (props) => {
  const {
    classname,
    target,
    date,
    technique,
    instrument,
    analysis = [],
    sample,
    data,
  } = props;

  const instruName = instrument ? instrument.name : "";
  const sampleName = sample ? `${sample.name}` : "";

  const Irradiation = data && data.Irradiation ? data.Irradiation : null;
  const FCS = data && data.FCS ? data.FCS : null;

  const analysisName = analysis.length > 1 ? "Analyses" : "Analysis";
  const analysisCount = analysis.length + " " + analysisName;

  return h(`div.${classname}`, [
    h("div.card-header", [h(PageViewDate, { date }), h("div", sampleName)]),
    h("div.bod", [
      h.if(FCS)("div", [FCS]),
      h("div", [h("span", technique)]),
      h("div", ["Instrument: " + instruName]),
      h.if(Irradiation)("div", [Irradiation]),
    ]),
    h("div.footer", [
      h.if(analysis.length > 1)("div", analysisCount),
      h("div", ["Target: " + target]),
    ]),
  ]);
};

const SessionListModelCard = (props) => {
  const {
    id,
    target,
    date,
    technique,
    instrument,
    analysis,
    sample,
    data,
    link,
    onClick,
    showIdentity,
    onHover = false,
  } = props;

  const classname = onHover ? "session-card-hover" : "session-card";

  const content = h(SessionListContent, {
    classname,
    target,
    date,
    technique,
    instrument,
    analysis,
    sample,
    data,
  });

  const cardContent = h(
    Frame,
    {
      id: "sessionCardContent",
      data: {
        id,
        target,
        date,
        technique,
        instrument,
        analysis,
        sample,
        data,
      },
    },
    content
  );

  return h(ModelCard, {
    id: id,
    content: cardContent,
    showIdentity,
    model: "session",
    link,
    onClick: () => onClick(id, date, target, technique),
  });
};

const SessionModelLinkCard = (props) => {
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

  const classname = onHover ? "session-card-hover" : "session-card";

  const content = h(SessionListContent, {
    classname,
    target,
    date,
    technique,
    instrument,
    analysis,
    sample,
    data,
  });

  const cardContent = h(
    Frame,
    {
      id: "sessionCardContent",
      data: {
        session_id,
        target,
        date,
        technique,
        instrument,
        analysis,
        sample,
        data,
      },
    },
    content
  );

  return h(ModelCard, {
    id: session_id,
    content: cardContent,
    model: "session",
    link,
    onClick: () => onClick(session_id, date, target, technique),
  });
};

const DataFileModelCard = (props) => {
  const { file_hash, basename, type, date } = props;

  const content = h("div.session-card", [
    h("div.card-header", [h(PageViewDate, { date })]),
    h("div.bod", [h("div", [h("span", basename)]), h("div", [type])]),
  ]);

  const dataFile = { file_hash, basename, type, date };

  const cardContent = h(
    Frame,
    {
      id: "dataFileCardContent",
      data: { dataFile },
    },
    content
  );

  return h(ModelCard, {
    id: file_hash,
    content: cardContent,
    model: "data-file",
  });
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
  SessionModelLinkCard,
  SessionListModelCard,
  DataFileModelCard,
  PublicationModelCard,
};
