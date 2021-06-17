import { useContext, useEffect, useState } from "react";
import { Frame } from "~/frame";
import { useAuth } from "~/auth";
import hyper from "@macrostrat/hyper";
import {
  APIHelpers,
  ModelEditor,
  useModelEditor,
} from "@macrostrat/ui-components";
import { APIV2Context } from "~/api-v2";
import { put } from "axios";
import { SampleContextMap } from "~/components";
import { MapLink } from "~/map";
import {
  EditNavBar,
  ModelEditableText,
  NewSampleMap,
  SampleLocation,
  SampleDepth,
  SampleElevation,
  GeoContext,
  SampleMaterial,
  ProjectAdd,
  SessionAdd,
  EmbargoDatePick,
  EditStatusButtons,
  DataSheetButton,
  NewSamplePageButton,
  TagContainer,
} from "../components";
import { SampleAdminContext } from "~/admin/sample";
import styles from "./module.styl";

const h = hyper.styled(styles);

const EmbargoEditor = function (props) {
  const { model, actions, isEditing } = useModelEditor();
  const onChange = (date) => {
    actions.updateState({
      model: { embargo_date: { $set: date } },
    });
  };
  const embargo_date = model.embargo_date;

  return h(EmbargoDatePick, { onChange, embargo_date, active: isEditing });
};

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
    editButtons: h("div", { style: { display: "flex" } }, [
      h(NewSamplePageButton),
      h(EditStatusButtons, {
        onClickCancel,
        onClickSubmit,
        hasChanges,
        isEditing,
      }),
    ]),
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

const LocationBlock = function (props) {
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

const Material = function (props) {
  const { isEditing, hasChanges, actions, model } = useModelEditor();

  const changeMaterial = (material) => {
    actions.updateState({
      model: { material: { $set: material } },
    });
  };
  if (isEditing) {
    return h(SampleMaterial, { changeMaterial, sample: model });
  }
  if (!isEditing) {
    if (model.material == null) return null;
    return h(Parameter, {
      name: "Material",
      value: model.material,
    });
  }
};

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
  const { isEditing, model, actions } = useModelEditor();

  const { sample_geo_entity } = model;

  const changeGeoEntity = (entity) => {
    const currnetEntities = [...sample_geo_entity];
    const newEntities = [...currnetEntities, ...new Array(entity)];
    actions.updateState({
      model: { sample_geo_entity: { $set: newEntities } },
    });
  };

  const deleteGeoEntity = (index) => {
    const currnetEntities = [...sample_geo_entity];
    currnetEntities.splice(index, 1);
    actions.updateState({
      model: { sample_geo_entity: { $set: currnetEntities } },
    });
  };

  return h(GeoContext, {
    sample_geo_entity,
    isEditing,
    changeGeoEntity,
    deleteGeoEntity,
  });
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
    if (isEditing) {
      changeFunction(addProject);
    }
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

  const changeCoordinates = (coords) => {
    const { lat, lon } = coords;
    const newLoc = {
      type: "Point",
      coordinates: [parseFloat(lon), parseFloat(lat)],
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

function SampleTagContainer() {
  const { model, actions, isEditing } = useModelEditor();

  const onAdd = (item) => {
    const currentTags = [...model.tags_tag];
    currentTags.push(item);
    console.log(currentTags);
    actions.updateState({
      model: { tags_tag: { $set: currentTags } },
    });
  };

  return h(TagContainer, { isEditing, tags: model.tags_tag, onChange: onAdd });
}

async function TagsChangeSet(changeset, updatedModel, url) {
  /**
   * tag_ids = data['tag_ids']
        for tag_id in tag_ids:
            params = {"jointable":f"tags.{model}_tag", "model_id_column":f"{model}_id",\
            "model_id": data['model_d'], "tag_id":tag_id}
   */
  if (changeset.tags_tag) {
    let { id } = updatedModel;
    const model_id = id;
    const tags = changeset.tags_tag;
    const tag_ids = tags.map((tag) => tag.id);
    const body = { model_id: model_id, tag_ids: tag_ids };
    const res = await put(url, body);
    const { data } = res;
    return data;
  }
  return "no tags";
}

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
        console.log("changeset", changeset);
        console.log("updatedModel", updatedModel);
        console.log(
          "Tags",
          TagsChangeSet(
            changeset,
            updatedModel,
            buildURL("/tags/models/sample", {})
          )
        );
        let rest;
        let { id } = updatedModel;
        const response = await put(
          buildURL(`/models/sample/${id}`, {}),
          updatedModel
        );
        const { data } = response;
        console.log(data);
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
        h.if(Edit)(SampleTagContainer),
        h("div.flex-row", [
          h("div.info-block", [
            Edit ? h(DataSheetButton) : null,

            h(GeoEntity),
            h(Material),
            h(DepthElevation),
            h("div.basic-info", [h(SampleProjectAdd), h(SampleSessionAdd)]),
            h(Frame, { id: "samplePage", data: sample.data }, null),
          ]),
          h("div", [h(LocationBlock)]),
        ]),
      ]),
    ]
  );
}

export { SamplePage };
