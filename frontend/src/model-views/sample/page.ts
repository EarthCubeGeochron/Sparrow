/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import * as React from "react";
import { useState, ReactNode } from "react";
import { useAuth } from "~/auth";
import hyper from "@macrostrat/hyper";
import {
  APIResultView,
  ModelEditorContext,
  LinkCard,
  useAPIResult,
  useModelEditor,
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
  EditableText,
} from "@blueprintjs/core";
import {
  MapSelector,
  MaterialSuggest,
} from "../../admin/data-sheet/sheet-enter-components";
import { useToggle } from "../../map/components/APIResult";
import { MultipleSelectFilter } from "../../filter/components";
import { useModelURL } from "~/util/router";
import { SampleEditing } from "./editor";
import { GeologicFormationSelector } from "../../filter/components/MultiSelect";
import {
  ModelEditor,
  ModelEditButton,
  CancelButton,
  SaveButton,
  APIHelpers,
} from "@macrostrat/ui-components";
import { EditNavBar, ModelEditableText } from "../project/editor";
import { SessionInfo } from "../data-files/page";
import { isSameDay } from "date-fns";

const h = hyper.styled(styles);

export const DOIPaperAdd = (props) => {
  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );
  const { setPubs } = props;
  const [search, setSearch] = React.useState<string | "">();
  const [click, setClick] = React.useState(false);
  console.log("search: ", search);

  const url = "https://xdd.wisc.edu/api/articles";

  const publication = useAPIResult(url, { doi: search });
  console.log(publication);

  React.useEffect(() => {
    if (click && search.length > 0) {
      try {
        const title = publication.success.data.map((pub) => {
          return { title: pub.title, doi: search };
        });
        setPubs(title);
      } catch (error) {}
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
  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );
  const { publication, onEdit, changeEdit } = props;
  const [pubs, setPubs] = React.useState([]);

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

  if ((!onEdit && pubs.length > 0) || (!isEditing && pubs.length > 0)) {
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
  if (isEditing) {
    return h("div", [
      h("h4.subtitle", ["Add Publications Publications"]),
      h(DOIPaperAdd, { setPubs: addPubs }),
    ]);
  }
  return null;
};

const Parameter = ({ name, value, ...rest }) => {
  return h("div.parameter", rest, [
    h("div", { style: { display: "flex", flexDirection: "row" } }, [
      h("h4.subtitle", name),
    ]),
    h("p.value", null, value),
  ]);
};

const ProjectLink = function({ d }) {
  const project = d.data.session.map((obj) => {
    if (obj.project !== null) {
      const { name: project_name, id: project_id } = obj.project;
      return { project_name, project_id };
    }
    return null;
  });

  const [test] = project;
  if (test == null) {
    return h(Button, { minimal: true }, ["No Projects"]);
  }

  const [{ project_name, project_id }] = project;

  const to = useModelURL(`/project/${project_id}`);

  return h(
    LinkCard,
    {
      to,
    },
    project_name
  );
};

const ProjectInfo = ({ sample: d }) => {
  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );
  const project = d.data.session.map((obj) => {
    if (obj.project !== null) {
      const { name: project_name, id: project_id } = obj.project;
      return { project_name, project_id };
    }
    return null;
  });

  const [test] = project;
  if (test == null) {
    if (isEditing) {
      return h("div.parameter", [
        h("h4.subtitle", "Project"),
        h("p.value", [
          h(Button, { minimal: true, rightIcon: "plus" }, ["Add Projects"]),
        ]),
      ]);
    }
    return null;
  }
  return h("div.parameter", [
    h("h4.subtitle", "Project"),
    h("p.value", [h(ProjectLink, { d })]),
  ]);
};

const LocationBlock = function (props) {
  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );
  const [open, toggleOpen] = useToggle(false);

  const { location, location_name } = props;

  if (location == null) {
    if (isEditing) {
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
    return null;
  }
  const zoom = 8;
  const [longitude, latitude] = location.coordinates;
  return h("div.location", [
    h(MapLink, { zoom, latitude, longitude }, [
      h(SampleContextMap, {
        center: location.coordinates,
        zoom,
      }),
    ]),
    h.if(location_name)("h5.location-name", location_name),
  ]);
};

const Material = function (props) {
  const { material, changeEdit, onEdit } = props;
  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );
  if (onEdit || isEditing) {
    return h("div", [h("h4.subtitle", ["Add Material"]), h(MaterialSuggest)]);
  }
  if (!onEdit || !isEditing) {
    if (material == null) return null;
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

function DataSheetButton() {
  const url = "/admin/data-sheet";
  const handleClick = (e) => {
    e.preventDefault();
    window.location.href = url;
  };

  return h("div", { style: { padding: "0px 5px 5px 0px" } }, [
    h(Button, { onClick: handleClick }, ["Data Sheet View"]),
  ]);
}

function SampleTags() {
  const [onEdit, setOnEdit] = useState(false);
  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );

  const tags = [
    "Needs Work",
    "Check Location",
    "Link to Publication",
    "Link to Project",
    "Add material",
  ];

  if (onEdit || isEditing) {
    return h("div", [
      h("h4.subtitle", ["Sample Tags"]),
      h(MultipleSelectFilter, {
        items: tags,
        sendQuery: () => null,
      }),
    ]);
  }
  if (!onEdit || !isEditing) {
    return h("div", [
      h("h4.subtitle", ["Sample Tags"]),
      h(
        Button,
        { minimal: true, rightIcon: "plus", onClick: () => setOnEdit(true) },
        ["Add Tags"]
      ),
    ]);
  }
}

function Sessions(props) {
  const { isEditing } = useModelEditor();

  const { session } = props;
  if (session.length == 0) {
    if (isEditing) {
      return h("div.parameter", [
        h("h4.subtitle", "Session"),
        h("p.value", [
          h(Button, { minimal: true, rightIcon: "plus" }, ["Add Sessions"]),
        ]),
      ]);
    }
    return null;
  }
  return h("div.parameter", [
    h("h4.subtitle", "Session"),
    h("p.value", [
      session.map((obj) => {
        const { id: session_id, technique, target, date } = obj;
        return h(SessionInfo, { session_id, technique, target, date });
      }),
    ]),
  ]);
}

function MetadataHelpers(props) {
  const { isEditing } = useModelEditor();
  const { name } = props;
  if (!isEditing) {
    return null;
  }
  if (isEditing) {
    return h("div", { style: { paddingTop: "30px" } }, [
      "Metadata Helpers:",
      //  h(GeoDeepDiveCard, { name }),
      h(GeologicFormationSelector),
      h(GeoDeepDiveCard, { sample_name: name }),
    ]);
  }
}

const SamplePage = function (props) {
  const [edit, setEdit] = React.useState(false);
  const { login } = useAuth();

  const { isEditing, hasChanges, actions } = React.useContext(
    ModelEditorContext
  );
  const changed = hasChanges;

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

  const { data: sample, Edit } = props;
  const { name, material, session, location, location_name } = sample.data;
  return h(
    ModelEditor,
    {
      model: sample.data,
      canEdit: login || Edit,
      persistChanges: () => null,
    },
    [
      h("div.sample", [
        h(
          "h2.page-type",
          { style: { display: "flex", justifyContent: "center" } },
          [Edit ? h(EditNavBar, { header: "Manage Sample" }) : null]
        ),
        h("div.flex-row", [
          h("div.info-block", [
            h(ModelEditableText, {
              is: "h3",
              field: "name",
              multiline: true,
            }),
            Edit ? h(DataSheetButton) : null,

            h("div.basic-info", [
              h(ProjectInfo, { sample }),
              h(Material, { material, changeEdit, onEdit: edit }),
              h(Sessions, {
                session,
              }),
              h(Publications, { publication: [], onEdit: edit, changeEdit }),
              Edit ? h(SampleTags, { onEdit: edit, changeEdit }) : null,
            ]),
          ]),
          h(
            "div",
            {
              style: {
                display: "flex",
                flexDirection: "column",
                paddingTop: "30px",
              },
            },
            [
              h(LocationBlock, { location, location_name }),
              h(MetadataHelpers, { sample_name: name }),
            ]
          ),
        ]),
        // h("h3", "Metadata helpers"),
        // find a better place for this
      ]),
    ]
  );
};

export { SamplePage };
