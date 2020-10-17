import hyper from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { FilterListComponent } from "app/components/filter-list";
import styles from "./module.styl";
import { useRouteMatch } from "react-router-dom";
import { useAPIResult } from "@macrostrat/ui-components";
import { SamplePage } from "./page";
import { useModelURL } from "~/util/router";

const h = hyper.styled(styles);

/**
 *
 * @param props : material, id, name (from samples)
 *
 *
 */
const SampleListCard = function(props) {
  const { material, id, name } = props;

  const to = useModelURL(`/sample/${id}`);

  return h(
    LinkCard,
    {
      to,
      key: id,
      className: "sample-list-card",
    },
    [
      h("h4", ["Sample ", h("span.name", name)]),
      h.if(material != null)("div.material", material),
    ]
  );
};

const SampleList = function() {
  const route = "/sample";
  const filterFields = {
    name: "Sample name",
    material: "Material",
    project_name: "Project",
  };

  return h("div.data-view.sample-list", [
    h(
      Callout,
      {
        icon: "info-sign",
        title: "Samples",
      },
      "This page lists all samples indexed in the laboratory data system."
    ),

    h(FilterListComponent, {
      route,
      filterFields,
      itemComponent: SampleListCard,
    }),
  ]);
};

interface sample {
  Edit?: boolean;
  id?: number;
  sendQuery: () => {};
}
const SampleComponent = function(props: sample) {
  const { id, Edit } = props;

  const url = `http://localhost:5002/api/v2/models/sample/${id}`;

  const data = useAPIResult(url, { nest: "session,project" });
  if (id == null || data == null) {
    return null;
  }

  //const sample = data[0];
  return h("div.data-view.project", null, h(SamplePage, { data, Edit }));
};

function SampleMatch({ Edit }) {
  const {
    params: { id },
  } = useRouteMatch();
  return h(SampleComponent, { id, Edit });
}

export { SampleList, SampleListCard, SampleMatch, SampleComponent };
