import { useContext, useEffect, useState } from "react";
import { Frame } from "~/frame";
import { useAuth } from "~/auth";
import hyper from "@macrostrat/hyper";
import { ModelEditor, useModelEditor } from "@macrostrat/ui-components";
import { Navbar, Spinner } from "@blueprintjs/core";
import { usePostgRESTResult } from "~/api/postgrest";
import { normalizeSample, useSampleModel } from "~/api/models";
import { useModelPersist } from "~/api/editing";
import { SampleContextMap, MinimalNavbar } from "~/components";
import { ModelTitleBar } from "~/model-views/components/page-view";
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
  NewModelButton,
  ModelAttributeOneLiner,
  TagContainer,
  PageViewBlock,
  DataFilePage,
  SubSamplePageView,
  FormattedLngLat,
  SampleCard,
} from "../components";
import { SampleAdminContext } from "~/admin/sample";
import styles from "./module.styl";
import { useModelURL } from "~/util";
import { Button } from "@blueprintjs/core";
import { MapDrawer } from "~/map/components/MapDrawer";

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

  return h("div.flex-row", [
    h(
      MinimalNavbar,
      null,
      h("div.editor-buttons", { style: { display: "flex" } }, [
        h(EditStatusButtons, {
          onClickCancel,
          onClickSubmit,
          hasChanges,
          isEditing,
        }),
        h(EmbargoEditor, {
          active: isEditing,
        }),
        h(Navbar.Divider),
        h(NewModelButton, { model: "sample", minimal: true }),
      ])
    ),
  ]);
};

const LocationBlock = function (props) {
  const { isEditing, hasChanges, actions, model } = useModelEditor();

  const { location, location_name } = model;

  if (isEditing) {
    return h(SampleLocationEleDepthEditor);
  }
  if (location == null) {
    return h(ModelAttributeOneLiner, {
      title: "Location: ",
      content: location,
    });
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
    h(FormattedLngLat, { location }),
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
    return h(ModelAttributeOneLiner, {
      title: "Material: ",
      content: model.material,
    });
  }
};

function MemberOfCard(props) {
  const { id, ...rest } = props;
  const sample = usePostgRESTResult(
    "/sample",
    { id: `eq.${id}` },
    { unwrap: (rows) => (rows.length > 0 ? normalizeSample(rows[0]) : null) }
  );
  if (sample == null) return `Sample ${id}`;
  return h(SampleCard, { ...sample, ...rest });
}

const MemberOf = function (props) {
  const { isEditing, hasChanges, actions, model } = useModelEditor();
  const { setListName, changeFunction } = useContext(SampleAdminContext);

  const sample = model;
  const memberOf = model.member_of;
  const href = useModelURL(`/sample/${memberOf}`);

  const onClickSample = (sample) => {
    const { id } = sample;
    actions.updateState({
      model: { member_of: { $set: id } },
    });
  };

  const onClickList = () => {
    setListName("sample");
    changeFunction(onClickSample);
  };

  let content;
  if (isEditing) {
    content = h("div", [
      h(Button, { onClick: onClickList, minimal: true, intent: "primary" }, [
        memberOf ? `Change from Sample ${memberOf}` : "Choose Parent Sample",
      ]),
    ]);
  } else {
    content = memberOf ? h(MemberOfCard, { id: memberOf, link: true }) : null;
  }

  return h(ModelAttributeOneLiner, {
    title: "Member of:",
    content,
  });
};

const SubSamples = function () {
  const { isEditing, hasChanges, actions, model } = useModelEditor();

  return h(SubSamplePageView, { sample_id: model.id, isEditing });
};

const DepthElevation = (props) => {
  const { isEditing, actions, model } = useModelEditor();

  const { depth, elevation } = model;

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

  if (isEditing) {
    return h("div", [
      h(SampleDepth, { sample: model, changeDepth }),
      h(SampleElevation, { sample: model, changeElevation }),
    ]);
  }
  return h("div.depth-elevation", [
    h(ModelAttributeOneLiner, {
      title: "Depth: ",
      content: depth,
    }),
    h(ModelAttributeOneLiner, {
      title: "Elevation: ",
      content: elevation,
    }),
  ]);
};

// TODO: re-enable once the API exposes geo_entity, sample_geo_entity and project_sample
const canEditLinks = false;

const GeoEntity = (props) => {
  const { isEditing: editing, model, actions } = useModelEditor();
  const isEditing = editing && canEditLinks;

  const { sample_geo_entity } = model;

  const changeGeoEntity = (entity) => {
    const currentEntities = [...sample_geo_entity];
    const newEntities = [...currentEntities, ...new Array(entity)];
    actions.updateState({
      model: { sample_geo_entity: { $set: newEntities } },
    });
  };

  const deleteGeoEntity = (index) => {
    const currentEntities = [...sample_geo_entity];
    currentEntities.splice(index, 1);
    actions.updateState({
      model: { sample_geo_entity: { $set: currentEntities } },
    });
  };

  let title: string =
    sample_geo_entity.length == 0 ? "Context" : "Geologic Context";

  return h(PageViewBlock, { title }, [
    h(LocationBlock),
    h(DepthElevation),
    h(GeoContext, {
      sample_geo_entity,
      isEditing,
      changeGeoEntity,
      deleteGeoEntity,
    }),
  ]);
};

const SampleProjectAdd = () => {
  const { model, actions, isEditing: editing } = useModelEditor();
  const isEditing = editing && canEditLinks;
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
  const { model, actions, isEditing: editing } = useModelEditor();
  const isEditing = editing && canEditLinks;
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
    ]
  );
};

function SampleTagContainer() {
  const { model, actions, isEditing } = useModelEditor();

  const onAdd = (item) => {
    const currentTags = [...model.tags_tag];
    currentTags.push(item);
    actions.updateState({
      model: { tags_tag: { $set: currentTags } },
    });
  };

  const onDelete = (id) => {
    const currentTags = [...model.tags_tag];
    const newTags = currentTags.filter((tag) => tag.id != id);
    actions.updateState({
      model: { tags_tag: { $set: newTags } },
    });
  };

  return h(TagContainer, {
    isEditing,
    tags: model.tags_tag,
    onChange: onAdd,
    onClickDelete: onDelete,
    modelName: "sample",
  });
}

const SamplePageDataFiles = () => {
  const { model } = useModelEditor();

  return h(DataFilePage, {
    model: "sample",
    session_ids: model.session.map((obj) => obj.id),
    sample_ids: [model.id],
  });
};

function TitleBar() {
  const { model } = useModelEditor();
  const id = model.id;
  return h(ModelTitleBar, {
    titleField: "name",
    subtitle: `Sample #${id}`,
    editingContent: h(EditNavBarSample),
  });
}

interface SampleProps {
  Edit?: boolean;
  id?: number;
  sendQuery?: () => {};
}
function SamplePage(props: SampleProps) {
  const { id, Edit } = props;
  if (id == null) return null;

  const { login } = useAuth();
  const persistChanges = useModelPersist("sample");

  const sample = useSampleModel(id);
  if (sample == null) {
    return h(Spinner);
  }

  /*
  Render sample page based on ID provided in URL through react router
  */

  return h(
    "div.data-view.sample",
    null,
    h(
      ModelEditor,
      {
        model: sample,
        canEdit: login || Edit,
        persistChanges,
      },
      [
        h("div.sample", [
          h(TitleBar),
          h(PageViewBlock, [
            h("div.flex-row", [
              h("div.info-block", [
                h(LabIDField),
                h(LabOwnerField),
                h(MemberOf),
                h(Material),
                h.if(Edit)(SampleTagContainer),
              ]),
              h("div", null, [
                h(Frame, { id: "sampleHeaderExt", data: { sample } }, null),
              ]),
            ]),
          ]),
        ]),
        h(SubSamples),
        h(SampleSessionAdd),
        h(SamplePageDataFiles),
        h(SampleProjectAdd),
        h(GeoEntity),
        h(Frame, { id: "samplePage", data: sample }, null),
      ]
    )
  );
}

function LabIDField() {
  const { model } = useModelEditor();
  const { lab_id } = model;
  return h.if(model.lab_id != null)(ModelAttributeOneLiner, {
    title: "Lab ID",
    content: model.lab_id,
  });
}

function LabOwnerField() {
  const { model } = useModelEditor();
  const { lab_owner } = model;
  return h.if(model.lab_owner != null)(ModelAttributeOneLiner, {
    title: "Lab Owner",
    content: model.lab_owner,
  });
}

export { SamplePage };
