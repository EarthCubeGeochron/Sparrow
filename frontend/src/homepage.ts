import { hyperStyled } from "@macrostrat/hyper";
import { Frame } from "./frame";
import { InsetText } from "app/components/layout";
// @ts-ignore
import styles from "./styles.module.css";
import loadable from "@loadable/component";
import { usePostgRESTResult } from "~/api/postgrest";

//import { SampleMap } from "../plugins/globe";
//import { useContext } from "react";

const MapHome = loadable(async function () {
  const module = await import("./map");
  return module.MapHome;
});

const h = hyperStyled(styles);

const metricLabels = {
  number_of_projects: "Projects",
  number_of_samples: "Samples",
  number_of_sessions: "Analytical sessions",
  number_of_analyses: "Analyses",
  samples_with_location: "Located samples",
};

function LabMetrics() {
  const metrics = usePostgRESTResult("/metrics", {}, { unwrap: (d) => d[0] });
  if (metrics == null) return null;
  return h(
    "ul.lab-metrics",
    Object.entries(metricLabels).map(([key, label]) =>
      h("li.metric", { key }, [
        h("span.value", metrics[key] ?? 0),
        h("span.label", label),
      ])
    )
  );
}

const HomePage = () => {
  return h("div.homepage", [
    h(InsetText, [
      h(
        Frame,
        { id: "landingText" },
        "This is where your lab's description text can go"
      ),
      h(Frame, { id: "landingMetrics" }, h(LabMetrics)),
      h(Frame, { id: "landingGraphic" }, h(MapHome)),
    ]),
  ]);
};

export default HomePage;
