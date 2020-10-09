/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import * as React from "react";
import { useState, ReactNode } from "react";

import hyper from "@macrostrat/hyper";
import {
  APIResultView,
  LinkCard,
  useAPIResult,
} from "@macrostrat/ui-components";
import { Link } from "react-router-dom";
import { SampleContextMap } from "app/components";
import { GeoDeepDiveCard } from "./gdd-card";
import styles from "./module.styl";
import { MapLink } from "app/map";
import { MapToaster } from "../../map/map-area";
import {
  Button,
  Icon,
  ControlGroup,
  InputGroup,
  Dialog,
} from "@blueprintjs/core";
import {
  MapSelector,
  MaterialSuggest,
} from "../../admin/data-sheet/sheet-enter-components";
import { useToggle } from "../../map/components/APIResult";
import { MultipleSelectFilter } from "../../filter/components";
import { useModelURL } from "~/util/router";

const h = hyper.styled(styles);

export const DOIPaperAdd = (props) => {
  const { setPubs } = props;
  const [search, setSearch] = React.useState<string | "">();
  const [click, setClick] = React.useState(false);
  console.log("search: ", search);

  const url = "https://xdd.wisc.edu/api/articles";

  const publication = useAPIResult(url, { doi: search });
  console.log(publication);

  React.useEffect(() => {
    if (click && search.length > 0) {
      const title = publication.success.data.map((pub) => {
        return { title: pub.title, doi: search };
      });
      setPubs(title);
    }
  }, [click]);

  // we want to send an API call to the DOI API
  const onClick = () => {
    setClick(true);
  };

  const onChange = (e) => {
    setSearch(e.target.value);
  };

  return h(ControlGroup, [
    h(InputGroup, { onChange, placeholder: "Enter DOI..." }),
    h(Button, { minimal: true, icon: "search", onClick }),
  ]);
};

const Publications = (props) => {
  const { publication, onEdit, changeEdit } = props;
  const [pubs, setPubs] = React.useState([]);
  console.log(pubs);

  React.useEffect(() => {
    if (publication) {
      const titles = publication.map((pub) => {
        const { title, doi } = pub;
        return { title, doi };
      });
      setPubs(titles);
    }
  }, []);

  const addPubs = (newPubs) => {
    setPubs([...pubs, ...newPubs]);
  };

  if (!onEdit && pubs.length > 0) {
    return h("div", [
      h("h4.subtitle", ["Publications"]),
      pubs.map((pub) => {
        return h("div", { key: pub.doi }, [
          h("h4", [
            h("a", { href: `https://dx.doi.org/${pub.doi}` }, [pub.title]),
          ]),
        ]);
      }),
    ]);
  }
  if (onEdit) {
    return h("div", [
      h("h4.subtitle", ["Add Publications Publications"]),
      h(DOIPaperAdd, { setPubs: addPubs }),
    ]);
  }
  return h("div.parameter", [
    h("h4.subtitle", ["Publications"]),
    h(Button, { minimal: true, rightIcon: "plus", onClick: changeEdit }, [
      "Add Publications",
    ]),
    pubs.map((pub) => {
      return h("h5", [pub.title]);
    }),
  ]);
};

const Parameter = ({ name, value, ...rest }) => {
  return h("div.parameter", rest, [
    h("div", { style: { display: "flex", flexDirection: "row" } }, [
      h("h4.subtitle", name),
    ]),
    h("p.value", null, value),
  ]);
};

const ProjectLink = function({ d, onEdit, changeEdit }) {
  const { project_name, project_id } = d;
  const to = useModelURL(`/project/${project_id}`);

  if (project_name == null || project_id == null) {
    return h(
      Button,
      { minimal: true, rightIcon: "plus", onClick: changeEdit },
      ["Add Projects"]
    );
  }
  if (onEdit) {
  }
  if (!onEdit) {
    return h(
      LinkCard,
      {
        to,
      },
      project_name
    );
  }
};

const ProjectInfo = ({ sample: d, onEdit, changeEdit }) =>
  h("div.parameter", [
    h("h4.subtitle", "Project"),
    h("p.value", [h(ProjectLink, { d, onEdit, changeEdit })]),
  ]);

const LocationBlock = function(props) {
  const [open, toggleOpen] = useToggle(false);
  console.log(open);
  const { sample } = props;
  const { geometry, location_name } = sample;
  if (geometry == null) {
    return h("div", [
      ///h("h4.subtitle", ["Set Latitude and Longitude"]),
      h(Button, {
        rightIcon: "map-create",
        text: "Set Latitude and Longitude",
        onClick: toggleOpen,
      }),
      h(MapSelector, { open: open, toggle: toggleOpen }),
    ]);
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
  const { material, changeEdit, onEdit } = props;
  if (onEdit) {
    return h("div", [h("h4.subtitle", ["Add Material"]), h(MaterialSuggest)]);
  }
  if (!onEdit) {
    return h(Parameter, {
      name: "Material",
      value:
        material ||
        h(Button, { minimal: true, rightIcon: "plus", onClick: changeEdit }, [
          "Add Material",
        ]),
    });
  }
};

const Sessions = (props) => {
  const { session, setEdit, onEdit } = props;
  return h(Parameter, {
    name: "Session",
    value: session || h("em", "None"),
    setEdit,
  });
};

const EditButton = (props) => {
  const { onClick, onEdit } = props;
  if (onEdit) {
    return h("div", [
      h(Button, {
        minimal: true,
        icon: "floppy-disk",
        text: "Save",
        onClick,
        intent: "success",
      }),
      h(Button, {
        minimal: true,
        text: "Cancel",
        onClick,
        intent: "danger",
      }),
    ]);
  }
  return h(Button, {
    onClick,
    minimal: true,
    icon: "edit",
    text: "Edit",
  });
};

function SampleTags(props) {
  const { onEdit, changeEdit } = props;
  const tags = [
    "Needs Work",
    "Check Location",
    "Link to Publication",
    "Link to Project",
    "Add material",
  ];

  if (onEdit) {
    return h("div", [
      h("h4.subtitle", ["Sample Tags"]),
      h(MultipleSelectFilter, {
        items: tags,
        sendQuery: () => null,
      }),
    ]);
  }
  if (!onEdit) {
    return h("div", [
      h("h4.subtitle", ["Sample Tags"]),
      h(Button, { minimal: true, rightIcon: "plus", onClick: changeEdit }, [
        "Add Tags",
      ]),
    ]);
  }
}

const SamplePage = function(props) {
  const [edit, setEdit] = React.useState(false);

  const changeEdit = () => {
    setEdit(!edit);
  };
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
    h("h2.page-type", { style: { display: "flex" } }, [
      "Sample",
      h(EditButton, { onClick: changeEdit, onEdit: edit }),
    ]),
    h("div.flex-row", [
      h("div.info-block", [
        h("h1", name),
        h("div.basic-info", [
          h(ProjectInfo, { sample, onEdit: edit, changeEdit }),
          h(Material, { material, changeEdit, onEdit: edit }),
          //h(Sessions, { session }),
          h(Publications, { publication: [], onEdit: edit, changeEdit }),
          h(SampleTags, { onEdit: edit, changeEdit }),
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
