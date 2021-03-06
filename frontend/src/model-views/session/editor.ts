import { hyperStyled } from "@macrostrat/hyper";
import { ModelEditor, useModelEditor } from "@macrostrat/ui-components";
import { useAPIv2Result } from "~/api-v2";
import { useAuth } from "~/auth";
import {
  EmbargoDatePick,
  EditStatusButtons,
  EditNavBar,
} from "../project/editor";
import { Link } from "react-router-dom";
import { Breadcrumbs } from "@blueprintjs/core";
import { useModelURL, useModelURLBool } from "~/util/router";
import { SessionInfoCard } from "./info-card";
import styles from "./module.styl";

const h = hyperStyled(styles);

function EditableSessionInfoCard(props) {
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

  const onClickCancel = () => {
    actions.toggleEditing();
  };
  const onClickSubmit = () => {
    actions.persistChanges();
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

export function EditableSessionDetails(props) {
  const { id } = props;

  const Edit = useModelURLBool();

  const res = useAPIv2Result(`/models/session/${id}`, {
    nest: "sample,instrument,publication,project",
  });
  if (!res) return null;

  console.log(res);

  const { login } = useAuth();

  const to = useModelURL("/session");
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
      },
    },
    [
      h("div", [
        h.if(Edit)(SessionEditsNavBar, { header: "Manage Session Links" }),
        h(Breadcrumbs, { items: breadCrumbs }),
        h(EditableSessionInfoCard),
      ]),
    ]
  );
}
