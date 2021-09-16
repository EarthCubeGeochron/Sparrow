import hyper from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { FilterListComponent } from "~/components/filter-list";
//@ts-ignore
import styles from "./module.styl";
import { useModelURL } from "~/util/router";
import { SampleModelCard } from "../components/list-cards/utils";

const h = hyper.styled(styles);

/**
 * Catalog Page
 * @param props : material, id, name (from samples)
 *
 *
 */
const SampleListCard = function(props) {
  const { material, id, name, location } = props;

  const to = useModelURL(`/sample/${id}`);

  return h(
    LinkCard,
    {
      to,
      key: id,
      className: "sample-list-card"
    },
    [
      h("h4", ["Sample ", h("span.name", name)]),
      h.if(material != null)("div.material", material)
    ]
  );
};

//Catalog Page
const SampleList = function() {
  const route = "/sample";
  const filterFields = {
    name: "Sample name",
    material: "Material",
    project_name: "Project"
  };

  return h("div.data-view.sample-list", [
    h(
      Callout,
      {
        icon: "info-sign",
        title: "Samples"
      },
      "This page lists all samples indexed in the laboratory data system."
    ),

    h(FilterListComponent, {
      route,
      filterFields,
      itemComponent: SampleListCard
    })
  ]);
};

export { SampleList, SampleListCard, SampleModelCard };
