import h from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import { SessionInfoLink } from "~/model-views/session/info-card";
import { PostgRESTFilterList } from "../components/filter-list";

const SessionListComponent = function () {
  const route = "/session";
  const filterFields = {
    sample_name: "Sample",
    project_name: "Project",
    target: "Material",
    instrument_name: "Instrument",
    technique: "Technique",
    measurement_group_id: "Group",
  };

  return h("div.data-view#session-list", [
    h(
      Callout,
      {
        icon: "info-sign",
        title: "Analytical sessions",
      },
      "This page lists analytical sessions (individual instrument runs on a single sample)"
    ),
    h(PostgRESTFilterList, {
      route,
      filterFields,
      itemComponent: SessionInfoLink,
    }),
  ]);
};

export { SessionListComponent };
