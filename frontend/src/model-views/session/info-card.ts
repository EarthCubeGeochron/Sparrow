import h from "@macrostrat/hyper";
import { Card } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { parse, format } from "date-fns";
import { useModelURL } from "~/util/router";
import { ModelAttributeOneLiner } from "../components";

export const Sample = props => {
  const sampleTo = useModelURL(`/sample/${props.id}`);
  console.log(sampleTo);
  return h("div.sample", [
    h("h4.info", "Sample"),
    h("div.sample-id", [h("a", { href: sampleTo }, [props.name])]),
    h("div.target", props.target)
  ]);
};


export const SessionDate = props => {
  const { date } = props;

  if (!date) return null;

  return h(ModelAttributeOneLiner, {
    title: "Session Date:",
    content: format(date, "MMMM D, YYYY")
  });
};

export const Instrument = function(props) {
  const { instrument } = props;
  if (!instrument) return null;

  const { name, id } = instrument;

  return h(ModelAttributeOneLiner, {
    title: "Instrument:",
    content: name
  });
};

export const Target = props => {
  const { target } = props;

  if (!target) return null;

  return h(ModelAttributeOneLiner, {
    title: "Target:",
    content: target
  });
};

export const AnalysisNumber = props => {
  const { analysis } = props;

  return h(ModelAttributeOneLiner, {
    title: "Number of Analyses:",
    content: analysis.length
  });
};

export const Publication = publication => {
  if (!publication) return null;

  return;
};

export const Technique = function({ technique }) {
  if (technique == null) {
    return null;
  }
  return h(ModelAttributeOneLiner, {
    title: "Technique:",
    content: technique
  });
};

// const MeasurementGroup = function({ measurement_group_id }) {
//   if (typeof measurement_group === "undefined" || measurement_group === null) {
//     return null;
//   }
//   return h("div.group", [
//     h("h5.small-info", "Group"),
//     h("div", measurement_group_id),
//   ]);
// };

export const SessionProjects = props => {
  const { project } = props;
  console.log(project);

  if (!project) return null;

  const { name, id } = project;
  const projectTo = useModelURL(`/project/${id}`);

  return h("div.project", [
    h("h4", "Project"),
    h("div", null, [h("a", { href: projectTo }, name) || "—"])
  ]);
};

const SessionInfoComponent = function(props) {
  // add some links to Project, sample, etc
  const { id, sample, target, project, date: sdate } = props;
  const date = parse(sdate);
  console.log(props);

  const sampleId = sample ? sample.id : null;
  const sampleName = sample ? sample.name : null;

  return h([
    h("div.top", [
      h("h4.date", format(date, "MMMM D, YYYY")),
      h("div.expander")
    ]),
    h("div.session-info", [
      h(Technique, props),
      h(Instrument, props),
      h(Sample, { id: sampleId, name: sampleName, target }),
      h(SessionProjects, { project })
      //h(MeasurementGroup, props),
    ])
  ]);
};

const SessionInfoLink = function(props) {
  const { id } = props;

  const to = useModelURL(`/session/${id}`);

  return h(
    LinkCard,
    {
      to,
      key: id,
      className: "session-info-card"
    },
    h(SessionInfoComponent, props)
  );
};

const SessionInfoCard = function(props) {
  const { id } = props;
  return h(
    Card,
    {
      key: id,
      className: "session-info-card"
    },
    h(SessionInfoComponent, props)
  );
};

export { SessionInfoComponent, SessionInfoLink, SessionInfoCard };
