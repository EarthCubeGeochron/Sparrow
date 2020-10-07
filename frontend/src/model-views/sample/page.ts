/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import * as React from "react";
import hyper from "@macrostrat/hyper";
import { APIResultView, LinkCard } from "@macrostrat/ui-components";
import { Link } from "react-router-dom";
import { SampleContextMap } from "app/components";
import { GeoDeepDiveCard } from "./gdd-card";
import styles from "./module.styl";
import { MapLink } from "app/map";
import { MapToaster } from "../../map/map-area";

const h = hyper.styled(styles);

const Parameter = ({ name, value, ...rest }) =>
  h("div.parameter", rest, [h("h4.subtitle", name), h("p.value", null, value)]);

const ProjectLink = function({ project_name, project_id }) {
  if (project_name == null || project_id == null) {
    return h("em", "None");
  }
  return h(
    LinkCard,
    {
      to: `/catalog/project/${project_id}`,
    },
    project_name
  );
};

const ProjectInfo = ({ sample: d }) =>
  h("div.parameter", [
    h("h4.subtitle", "Project"),
    h("p.value", [h(ProjectLink, d)]),
  ]);

const LocationBlock = function(props) {
  const { sample } = props;
  const { geometry, location_name } = sample;
  if (geometry == null) {
    return null;
  }
  const zoom = 8;
  const [longitude, latitude] = geometry.coordinates;
  return h("div.location", [
    h(MapLink, { zoom, latitude, longitude }, [
      h(SampleContextMap, {
        center: geometry.coordinates,
        zoom,
      }),
    ]),
    h.if(location_name)("h5.location-name", location_name),
  ]);
};

const Material = function(props) {
  const { material } = props;
  return h(Parameter, {
    name: "Material",
    value: material || h("em", "None"),
  });
};

const SamplePage = function(props) {
  /*
  Render sample page based on ID provided in URL through react router
  */
  React.useEffect(() => {
    const onMap = window.location.pathname == "/map";
    if (!onMap) {
      MapToaster.clear();
    }
  }, [window.location.pathname]);

  //const { match } = props;
  const { sample } = props;
  const { name, material } = sample;
  return h("div.sample", [
    h("h3.page-type", "Sample"),
    h("div.flex-row", [
      h("div.info-block", [
        h("h2", name),
        h("div.basic-info", [
          h(ProjectInfo, { sample }),
          h(Material, { material }),
        ]),
      ]),
      h(LocationBlock, { sample }),
    ]),
    h("h3", "Metadata helpers"),
    h(GeoDeepDiveCard, { sample_name: name }),
    // find a better place for this
  ]);
};

export { SamplePage };
