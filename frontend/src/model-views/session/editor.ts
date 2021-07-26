import { useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  ModelEditor,
  useModelEditor,
  APIHelpers,
} from "@macrostrat/ui-components";
import { useAPIv2Result, APIV2Context } from "~/api-v2";
import { useAuth } from "~/auth";
import { put } from "axios";
import { useModelURL, useModelURLBool } from "~/util/router";
import {
  Instrument,
  Technique,
  Target,
  SessionDate,
  AnalysisNumber,
  SessionInfoCard,
} from "./info-card";
import {
  EditNavBar,
  SampleAdd,
  ProjectAdd,
  PubAdd,
  ModelEditableText,
  EmbargoDatePick,
  EditStatusButtons,
  TagContainer,
  PageViewBlock,
  DataFilePage,
} from "../components";
import { SessionAdminContext } from "~/admin/session";
import styles from "./module.styl";

const h = hyperStyled(styles);

function CatalogSessionInfoCard(props) {
  const { isEditing, hasChanges, model, actions } = useModelEditor();

  return h("div.test", [h(SessionInfoCard, model)]);
}

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

function SessionDataFiles(props) {
  const { model } = useModelEditor();

  return h(DataFilePage, { session_ids: [model.id], model: "session" });
}

function EditStatusButtonsSess(props) {
  const { isEditing, hasChanges, actions } = useModelEditor();
  const { setListName } = useContext(SessionAdminContext);

  const onClickCancel = () => {
    actions.toggleEditing();
    setListName("main");
  };
  const onClickSubmit = () => {
    actions.persistChanges();
    setListName("main");
  };

  return h(EditStatusButtons, {
    onClickCancel,
    onClickSubmit,
    hasChanges,
    isEditing,
  });
}

function SessionEditsNavBar(props) {
  const { header } = props;

  return h(EditNavBar, {
    header,
    editButtons: h(EditStatusButtonsSess),
    embargoEditor: h(EmbargoEditor),
  });
}

function SessionTagContainer() {
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
    modelName: "session",
  });
}

function SessionName(props) {
  const { model, isEditing, actions } = useModelEditor();

  if (!isEditing && model["name"] == null) {
    return h("h4", "No Name");
  }
  return h(ModelEditableText, {
    is: "h4",
    field: "name",
    multiline: true,
  });
}

function SessionPublication(props) {
  const { model, isEditing, actions } = useModelEditor();
  const { setListName, changeFunction } = useContext(SessionAdminContext);

  const onClickDelete = () => {
    actions.updateState({
      model: { publication: { $set: null } },
    });
  };

  const onClickPub = (id, title, doi) => {
    actions.updateState({
      model: { publication: { $set: { id, title, doi } } },
    });
  };

  const onClickList = () => {
    setListName("publication");
    changeFunction(onClickPub);
  };

  const data = model.publication ? [model.publication] : null;

  return h(PubAdd, {
    data,
    isEditing,
    onClickDelete,
    onClickList,
  });
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

function EditableSessionInfoComponent(props) {
  const { model, isEditing, actions } = useModelEditor();
  const { setListName, changeFunction } = useContext(SessionAdminContext);

  const { id, sample, project, date } = model;
  const onProjectClick = (id, name) => {
    actions.updateState({
      model: { project: { $set: { id, name } } },
    });
  };

  const onProjectClickDelete = () => {
    actions.updateState({
      model: { project: { $set: null } },
    });
  };

  const projectClickList = () => {
    setListName("project");
    changeFunction(onProjectClick);
  };

  const onSampleClick = (sample) => {
    actions.updateState({
      model: { sample: { $set: sample } },
    });
  };

  const onSampleClickDelete = (sample) => {
    actions.updateState({
      model: { sample: { $set: null } },
    });
  };

  const sampleListClick = () => {
    setListName("sample");
    changeFunction(onSampleClick);
  };

  const data = model.sample ? [sample] : null;

  return h("div", [
    h(PageViewBlock, [
      h("div.session-info", [
        h(SessionName),
        h(SessionDate, model),
        h(Technique, model),
        h(Instrument, model),
        h(Target, model),
        h(AnalysisNumber, model),
        h(SessionTagContainer),
      ]),
    ]),

    h(SampleAdd, {
      data,
      isEditing,
      onClickList: sampleListClick,
      onClickDelete: onSampleClickDelete,
    }),
    h(ProjectAdd, {
      isEditing,
      data: { project: [project] },
      onClickList: projectClickList,
      onClickDelete: onProjectClickDelete,
    }),
    h(SessionPublication),
    h(SessionDataFiles),
  ]);
}

export function EditableSessionDetails(props) {
  const { id } = props;

  const Edit = useModelURLBool();
  const res = useAPIv2Result(`/models/session/${id}`, {
    nest: "sample,instrument,project,tag,publication",
  });
  const { login } = useAuth();
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  if (!res) return null;

  return h(
    ModelEditor,
    {
      model: res.data,
      canEdit: login || Edit,
      persistChanges: async (updatedModel, changeset) => {
        console.log(updatedModel);
        console.log(changeset);
        TagsChangeSet(
          changeset,
          updatedModel,
          buildURL("/tags/models/session", {})
        );
        let rest;
        let { id } = updatedModel;
        const response = await put(
          buildURL(`/models/session/${id}`, {}),
          changeset
        );
        const { data } = response;
        ({ id, ...rest } = data);
        return rest;
      },
    },
    [
      h("div", [
        h.if(Edit)(SessionEditsNavBar, { header: `Manage Session #${id}` }),
        h.if(Edit)(EditableSessionInfoComponent),
        h.if(!Edit)(CatalogSessionInfoCard),
      ]),
    ]
  );
}
