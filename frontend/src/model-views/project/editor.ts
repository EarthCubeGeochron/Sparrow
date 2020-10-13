import { useContext, useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  EditableText,
  Intent,
  Switch,
  Alignment,
  Button,
  Popover,
  ButtonGroup,
} from "@blueprintjs/core";
import { useAuth } from "~/auth";
import {
  ModelEditor,
  ModelEditorContext,
  ModelEditButton,
  CancelButton,
  SaveButton,
  useModelEditor,
  APIContext,
  APIHelpers,
} from "@macrostrat/ui-components";
import { MinimalNavbar } from "~/components";
import { put } from "axios";
import "../main.styl";
import styles from "~/admin/module.styl";
const h = hyperStyled(styles);

const ModelEditableText = function(props) {
  let { multiline, field, placeholder, is, ...rest } = props;
  const el = is || "div";
  if (placeholder == null) {
    placeholder = "Add a " + field;
  }
  delete rest.is;
  const { model, actions, isEditing } = useContext(ModelEditorContext);

  // Show text with primary intent if changes have been made
  const intent = actions.hasChanges(field) ? Intent.SUCCESS : null;

  return h(el, rest, [
    h.if(isEditing)(EditableText, {
      className: `model-edit-text field-${field}`,
      multiline,
      placeholder,
      intent,
      onChange: actions.onChange(field),
      value: model[field],
    }),
    h.if(!isEditing)("span", model[field]),
  ]);
};

const EmbargoEditor = function(props) {
  const { login } = useAuth();
  const { model, actions } = useContext(ModelEditorContext);
  const [isOpen, setOpen] = useState(false);
  const text = model.embargo_date != null ? "Embargoed" : "Public";
  const icon = model.embargo_date != null ? "lock" : "unlock";
  if (!login) {
    return null;
  }
  return h("div.embargo-editor", [
    h(
      Popover,
      {
        position: "bottom",
        isOpen,
        onClose: (evt) => {
          console.log(evt);
          return setOpen(false);
        },
      },
      [
        h(Button, {
          text,
          minimal: true,
          interactive: false,
          rightIcon: icon,
          intent: Intent.SUCCESS,
          onClick() {
            return setOpen(!isOpen);
          },
        }),
        h("div.embargo-control-panel", [
          h(Switch, {
            checked: model.embargo_date != null,
            label: "Embargoed",
            alignIndicator: Alignment.RIGHT,
            onChange(evt) {
              const { checked } = evt.target;
              const val = checked ? "+Infinity" : null;
              return actions.persistChanges({ embargo_date: { $set: val } });
            },
          }),
        ]),
      ]
    ),
  ]);
};

const EditStatusButtons = function() {
  const { isEditing, hasChanges, actions } = useModelEditor();
  const changed = hasChanges();
  return h("div.edit-status-controls", [
    h.if(!isEditing)(ModelEditButton, { minimal: true }, "Edit"),
    h.if(isEditing)(ButtonGroup, { minimal: true }, [
      h(
        SaveButton,
        {
          disabled: !changed,
          onClick() {
            return actions.persistChanges();
          },
        },
        "Save"
      ),
      h(
        CancelButton,
        {
          intent: changed ? "warning" : "none",
          onClick: actions.toggleEditing,
        },
        "Done"
      ),
    ]),
  ]);
};

const EditNavBar = function(props) {
  return h(MinimalNavbar, { className: "project-editor-navbar" }, [
    h("h4", props.header),
    h(EditStatusButtons),
    h(EmbargoEditor),
  ]);
};

const EditableProjectDetails = function(props) {
  const { project } = props;
  const { login } = useAuth(); // this appears to be a boolean
  const { buildURL } = APIHelpers(useContext(APIContext));

  return h(
    ModelEditor,
    {
      model: project,
      canEdit: login,
      persistChanges: async (updatedModel, changeset) => {
        let rest;
        let { id } = updatedModel;
        const response = await put(buildURL(`/edit/project/${id}`), changeset);
        const { data } = response;
        ({ id, ...rest } = data);
        return rest;
      },
    },
    [
      h("div.project-editor", [
        h("div", { style: { display: "flex", justifyContent: "center" } }, [
          h(EditNavBar, { header: "Manage Project" }),
        ]),
        h("div.project-editor-content", [
          h(ModelEditableText, { is: "h3", field: "name", multiline: true }),
          h(ModelEditableText, {
            is: "p",
            field: "description",
            multiline: true,
          }),
        ]),
      ]),
    ]
  );
};

export { EditableProjectDetails, EditNavBar, ModelEditableText };
