/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "@macrostrat/hyper";
import { Card } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { parse, format } from "date-fns";
import { useModelURL } from "~/util/router";

const Sample = (props) => {
  const sampleTo = useModelURL(`/sample/${props.id}`);
  console.log(sampleTo);
  return h("div.sample", [
    h("h5.info", "Sample"),
    h("div.sample-id", [h("a", { href: sampleTo }, [props.name])]),
    h("div.target", props.target),
  ]);
};

const Instrument = function({ instrument_name }) {
  if (instrument_name == null) {
    return null;
  }
  return h("div.instrument", [
    h("h5.small-info", "Instrument"),
    h("div", instrument_name),
  ]);
};

const Technique = function({ technique }) {
  if (technique == null) {
    return null;
  }
  return h("div.technique", [
    h("h5.small-info", "Technique"),
    h("div", technique),
  ]);
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

const SessionInfoComponent = function(props) {
  // add some links to Project, sample, etc
  const {
    id,
    sample_id,
    sample_name,
    target,
    project_name,
    project_id,
  } = props;
  const date = parse(props.date);
  console.log(props);

  const projectTo = useModelURL(`/project/${project_id}`);

  return h([
    h("div.top", [
      h("h4.date", format(date, "MMMM D, YYYY")),
      h("div.expander"),
    ]),
    h("div.session-info", [
      h(Sample, { id: sample_id, name: sample_name, target }),
      h("div.project", [
        h("h5.info", "Project"),
        h("div", null, [h("a", { href: projectTo }, project_name) || "—"]),
      ]),
      h(Instrument, props),
      h(Technique, props),
      //h(MeasurementGroup, props),
    ]),
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
      className: "session-info-card",
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
      className: "session-info-card",
    },
    h(SessionInfoComponent, props)
  );
};

export { SessionInfoComponent, SessionInfoLink, SessionInfoCard };
