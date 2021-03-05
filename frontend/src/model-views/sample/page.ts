/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import { useContext, useEffect } from "react";
import { useAuth } from "~/auth";
import hyper from "@macrostrat/hyper";
import {
  APIHelpers,
  ModelEditor,
  useModelEditor,
} from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { put } from "axios";
import { SampleContextMap } from "app/components";
import { MapLink } from "app/map";
import { Button } from "@blueprintjs/core";
import {
  EditNavBar,
  EditStatusButtons,
  EmbargoEditor,
  ModelEditableText,
} from "../project/editor";
import { ProjectModelCard, SessionModelCard } from "../list-cards/utils";
import {
  NewSampleMap,
  SampleLocation,
  SampleDepth,
  SampleElevation,
  SampleGeoEntity,
  SampleMaterial,
  ProjectAdd,
  SessionAdd,
} from "../new-model";
import { ProjectEditCard, SessionEditCard } from "./detail-card";
import { SampleAdminContext } from "~/admin/sample";
import { DndContainer } from "~/components";
import styles from "./module.styl";

const h = hyper.styled(styles);

const EditNavBarSample = () => {
  const { hasChanges, actions, isEditing, model } = useModelEditor();
  const { setListName } = useContext(SampleAdminContext);

  const onClickCancel = () => {
    setListName("main");
    actions.toggleEditing();
  };
  const onClickSubmit = () => {
    setListName("main");
    return actions.persistChanges();
  };

  const onChange = (date) => {
    actions.updateState({
      model: { embargo_date: { $set: date } },
    });
  };
  const embargo_date = model.embargo_date;

  return h(EditNavBar, {
    header: "Manage Sample",
    editButtons: h(EditStatusButtons, {
      onClickCancel,
      onClickSubmit,
      hasChanges,
      isEditing,
    }),
    embargoEditor: h(EmbargoEditor, {
      onChange,
      embargo_date,
      active: isEditing,
    }),
  });
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
  const project = d.project.map((obj) => {
    if (obj) {
      const { name: project_name, id: project_id } = obj;
      return { project_name, project_id };
    }
    return null;
  });

  const [test] = project;
  if (test == null) return null;

  return project.map((ele) => {
    if (!ele) return null;
    const { project_name, project_id, description } = ele;
    return h(ProjectModelCard, {
      id: project_id,
      name: project_name,
      description,
      link: true,
    });
  });
};

export const SampleProjects = ({ data, isEditing, onClick }) => {
  //console.log(data);
  if (isEditing) {
    return h("div.parameter", [
      h("h4.subtitle", "Project"),
      h("p.value", [h(ProjectEditCard, { d: data, onClick })]),
    ]);
  }
  return h("div.parameter", [
    h("h4.subtitle", "Project"),
    h("p.value", [h(ProjectLink, { d: data })]),
  ]);
};

const LocationBlock = function(props) {
  const { isEditing, hasChanges, actions, model } = useModelEditor();

  const { location, location_name } = model;

  if (isEditing) {
    return h(SampleLocationEleDepthEditor);
  }
  if (location == null) {
    return null;
  }
  const zoom = 8;
  const [longitude, latitude] = location.coordinates;
  return h("div.location", [
    h("h5.lon-lat", `[${longitude} , ${latitude}]`),
    h(MapLink, { zoom, latitude, longitude }, [
      h(SampleContextMap, {
        center: location.coordinates,
        zoom,
      }),
    ]),
    h.if(location_name)("h5.location-name", location_name),
  ]);
};

const Material = function(props) {
  const { isEditing, hasChanges, actions, model } = useModelEditor();

  const changeMaterial = (material) => {
    actions.updateState({
      model: { material: { $set: material } },
    });
  };
  if (isEditing) {
    return h(SampleMaterial, { changeMaterial, sample: model }); //material component from sample page
  }
  if (!isEditing) {
    if (model.material == null) return null;
    return h(Parameter, {
      name: "Material",
      value: model.material,
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

export function Sessions(props) {
  const {
    isEditing,
    session,
    onClick,
    sampleHoverID = null,
    onDrop = () => {},
  } = props;

  if (session == null && !isEditing) return null;
  if (session == null && isEditing) {
    return h("div.parameter", [h("h4.subtitle", "Sessions")]);
  }
  return h("div.parameter", [
    h("h4.subtitle", "Sessions"),
    h("div.session-container", [
      session.map((obj) => {
        const {
          id: session_id,
          technique,
          target,
          date,
          analysis,
          data,
          sample,
        } = obj;
        const onHover =
          sampleHoverID && sample ? sample.id == sampleHoverID : false;
        if (isEditing) {
          return h(
            DndContainer,
            {
              id: session_id,
              onDrop,
            },
            [
              h(SessionEditCard, {
                session_id,
                sample,
                technique,
                target,
                date,
                onClick,
                onHover,
              }),
            ]
          );
        } else {
          return h(SessionModelCard, {
            session_id,
            technique,
            target,
            date,
            data,
            analysis,
            sample,
            onHover,
          });
        }
      }),
    ]),
  ]);
}

const DepthElevation = (props) => {
  const { isEditing, model } = useModelEditor();

  const { depth, elevation } = model;

  return !isEditing
    ? h.if(elevation != null || depth != null)("div.depth-elevation", [
        h.if(depth != null)("div.parameter", [
          h("h4.subtitle", "Depth"),
          h("p.value", [depth]),
        ]),
        h.if(elevation != null)("div.parameter", [
          h("h4.subtitle", "Elevation"),
          h("p.value", [elevation]),
        ]),
      ])
    : null;
};

const GeoEntity = (props) => {
  const { isEditing, model } = useModelEditor();

  const { sample_geo_entity } = model; // going to be an array..

  if (!isEditing) {
    if (sample_geo_entity.length != 0) {
      return h("div.parameter", [
        h("h4.subtitle", "Geo Entity"),
        sample_geo_entity.map((ele) => {
          const { type, name } = ele.geo_entity;
          return h("p.value", [name + " " + type]);
        }),
      ]);
    } else {
      return null;
    }
  } else {
    return h(SampleGeoEntity, { geoEntity: "", changeGeoEntity: () => {} });
  }
};

const SampleProjectAdd = () => {
  const { model, actions, isEditing } = useModelEditor();
  const { setListName, changeFunction } = useContext(SampleAdminContext);

  const onClickDelete = ({ id, name }) => {
    const ps = [...model.project];
    const newPs = ps.filter((ele) => ele.id != id);
    actions.updateState({
      model: { project: { $set: newPs } },
    });
  };

  const addProject = (id, name) => {
    const projects = model.project ? [...model.project] : [];
    const proj = new Array({ id, name });
    const newProjs = [...projects, ...proj];
    actions.updateState({
      model: { project: { $set: newProjs } },
    });
  };

  useEffect(() => {
    changeFunction(addProject);
  }, [model.project]);

  const onClickList = () => {
    setListName("project");
    changeFunction(addProject);
  };

  return h(ProjectAdd, { data: model, isEditing, onClickDelete, onClickList });
};

const SampleSessionAdd = () => {
  const { model, actions, isEditing } = useModelEditor();
  const { setListName, changeFunction } = useContext(SampleAdminContext);

  const addSession = (id, date, target, technique) => {
    const currentSessions = [...model.session];
    const newSess = new Array({ id, date, target, technique });
    const newSessions = [...currentSessions, ...newSess];
    actions.updateState({
      model: { session: { $set: newSessions } },
    });
  };

  const onClickDelete = ({ session_id: id, date }) => {
    const ss = [...model.session];
    const newSs = ss.filter((ele) => ele.id != id);
    actions.updateState({
      model: { session: { $set: newSs } },
    });
  };

  const onClickList = () => {
    setListName("session");
    changeFunction(addSession);
  };

  return h(SessionAdd, {
    data: model.session,
    isEditing,
    onClickList,
    onClickDelete,
  });
};

const SampleLocationEleDepthEditor = () => {
  const { model, actions, isEditing } = useModelEditor();

  const loc = model.location ? model.location : { coordinates: [0, 0] };
  const [longitude, latitude] = loc.coordinates;

  const sample = { ...model, longitude, latitude };

  //console.log(longitude, latitude);

  const changeCoordinates = (coords) => {
    const { lat, lon } = coords;
    const newLoc = {
      tpye: "Point",
      coordinates: [lon, lat],
    };
    actions.updateState({
      model: { location: { $set: newLoc } },
    });
  };

  const changeDepth = (depth) => {
    actions.updateState({
      model: { depth: { $set: depth } },
    });
  };

  const changeElevation = (elev) => {
    actions.updateState({
      model: { elevation: { $set: elev } },
    });
  };

  return h(
    "div",
    { style: { justifyContent: "flex-end", minWidth: "405px" } },
    [
      h("div.sample-map", { style: { maxWidth: "455px" } }, [
        h(NewSampleMap, { changeCoordinates, sample: { longitude, latitude } }),
      ]),
      h(SampleLocation, {
        changeCoordinates,
        sample: { longitude, latitude },
        stacked: false,
      }),
      h("div", [
        h(SampleElevation, { sample, changeElevation }),
        h(SampleDepth, { sample, changeDepth }),
      ]),
    ]
  );
};

function SamplePage(props) {
  const { data: sample, Edit } = props;

  const { login } = useAuth();
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  /*
  Render sample page based on ID provided in URL through react router
  */

  return h(
    ModelEditor,
    {
      model: sample.data,
      canEdit: login || Edit,
      persistChanges: async (updatedModel, changeset) => {
        console.log(changeset);
        console.log(updatedModel);
        // let rest;
        // let { id } = updatedModel;
        // const response = await put(
        //   buildURL(`/models/sample/${id}`, {}),
        //   changeset
        // );
        // const { data } = response;
        // ({ id, ...rest } = data);
        // return rest;
      },
    },
    [
      h("div.sample", [
        h("div.page-type", [Edit ? h(EditNavBarSample) : null]),
        h(ModelEditableText, {
          is: "h3",
          field: "name",
          multiline: true,
        }),
        h("div.flex-row", [
          h("div.info-block", [
            Edit ? h(DataSheetButton) : null,

            h(GeoEntity),
            h(Material),
            h(DepthElevation),
            h("div.basic-info", [h(SampleProjectAdd), h(SampleSessionAdd)]),
          ]),
          h("div", [h(LocationBlock)]),
        ]),
      ]),
    ]
  );
}

export { SamplePage };
