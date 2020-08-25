/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import { Component } from "react";
import hyper from "@macrostrat/hyper";
import { Callout } from "@blueprintjs/core";
import { PagedAPIView, LinkCard } from "@macrostrat/ui-components";
import { FilterListComponent } from "app/components/filter-list";
import { SampleCard } from "./detail-card";
import { FilterMenu } from "../../map/components/filterMenu";
import styles from "./module.styl";

const h = hyper.styled(styles);

const SampleListCard = function (props) {
  const { material, id, name, location_name } = props;
  return h(
    LinkCard,
    {
      to: `/catalog/sample/${id}`,
      key: id,
      className: "sample-list-card",
    },
    [
      h("h4", ["Sample ", h("span.name", name)]),
      h("div.location-name", location_name),
      h.if(material != null)("div.material", material),
    ]
  );
};

const SampleList = function () {
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

export { SampleList };
