import { useContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  ModelEditor,
  useModelEditor,
  APIHelpers,
} from "@macrostrat/ui-components";
import { parse, format } from "date-fns";
import { useAPIv2Result, APIV2Context } from "~/api-v2";
import { useAuth } from "~/auth";
import { put } from "axios";
import {
  EmbargoDatePick,
  EditStatusButtons,
  EditNavBar,
} from "../project/editor";
import { Link } from "react-router-dom";
import { Breadcrumbs, Card } from "@blueprintjs/core";
import { useModelURL, useModelURLBool } from "~/util/router";
import {
  Instrument,
  Technique,
  SessionProjects,
  SessionInfoCard,
} from "./info-card";
import { SampleAdd, ProjectAdd, PubAdd } from "../new-model";
import { SessionAdminContext } from "~/admin/session";
import styles from "./module.styl";

const h = hyperStyled(styles);

function CatalogSessionInfoCard(props) {
  const { isEditing, hasChanges, model, actions } = useModelEditor();

  return h("div.test", [h(SessionInfoCard, model)]);
}

const EmbargoEditor = function(props) {
  const { model, actions, isEditing } = useModelEditor();
  const onChange = (date) => {
    actions.updateState({
      model: { embargo_date: { $set: date } },
    });
  };
  const embargo_date = model.embargo_date;

  return h(EmbargoDatePick, { onChange, embargo_date, active: isEditing });
};

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

function EditableSessionInfoComponent(props) {
  const { model, isEditing, actions } = useModelEditor();
  const { setListName, changeFunction } = useContext(SessionAdminContext);

  const { id, sample, project, date: sdate } = model;
  const date = parse(sdate);

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

  return h(Card, { id, className: "session-info-card" }, [
    h("div.top", [
      h("h4.date", format(date, "MMMM D, YYYY")),
      h("div.expander"),
    ]),
    h("div.session-info", [
      h(SampleAdd, {
        data,
        isEditing,
        onClickList: sampleListClick,
        onClickDelete: onSampleClickDelete,
      }),
      h.if(isEditing)(ProjectAdd, {
        isEditing,
        data: { project: [project] },
        onClickList: projectClickList,
        onClickDelete: onProjectClickDelete,
      }),
      h.if(!isEditing)(SessionProjects, { project }),
      h(Instrument, model),
      h(Technique, model),
      h(SessionPublication),
    ]),
  ]);
}

export function EditableSessionDetails(props) {
  const { id } = props;

  const Edit = useModelURLBool();
  const res = useAPIv2Result(`/models/session/${id}`, {
    nest: "sample,instrument,publication,project",
  });
  const { login } = useAuth();
  const { buildURL } = APIHelpers(useContext(APIV2Context));
  const to = useModelURL("/session");
  
  if (!res) return null;


  const breadCrumbs = [
    { text: h(Link, { to }, "Sessions") },
    { icon: "document", text: h("code.session-id", id) },
  ];

  return h(
    ModelEditor,
    {
      model: res.data,
      canEdit: login || Edit,
      persistChanges: async (updatedModel, changeset) => {
        console.log(updatedModel);
        console.log(changeset);
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
        h.if(Edit)(SessionEditsNavBar, { header: "Manage Session Links" }),
        h(Breadcrumbs, { items: breadCrumbs }),
        h.if(Edit)(EditableSessionInfoComponent),
        h.if(!Edit)(CatalogSessionInfoCard),
      ]),
    ]
  );
}
