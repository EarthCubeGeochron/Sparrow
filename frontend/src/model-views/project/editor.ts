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
import { ProjectPublications } from "./page";
import update from "immutability-helper";
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

/**
 * Component to display normal publication view, but on edit allow for the deletion, or addition of DOI's.
 * TODO: Have paper title appear, maybe in an alert or a tooltip, check to make sure it's the correct pub
 */
function EditablePublications(props) {
  const { isEditing, model, actions } = useModelEditor();

  // use the index returned to locate the object in publications and update it.
  // replace the old publcations with a new array in the model
  const onChangeHandler = (index, value) => {
    let newPublications = [...model.publications];
    newPublications[index] = { ...newPublications[index], doi: value };
    console.log(newPublications);
    return actions.updateState({
      model: { publications: { $set: newPublications } },
    });
  };

  // probably call a http delete here
  // but this call back will happen on an alert pop up as confirmation I think
  // it'll be a little strange since these saves will be separate from the model persistChanges()
  const handleDeletePub = ({ index }) => {
    let newPublications = [...model.publications];

    const { id, doi } = newPublications[index];
    console.log(doi);

    // this just gives the look
    newPublications.splice(index, 1);
    return actions.updateState({
      model: { publications: { $set: newPublications } },
    });
  };

  const DeleteButton = (index) =>
    h(Button, {
      icon: "trash",
      intent: "danger",
      minimal: true,
      onClick: () => handleDeletePub(index),
    });

  const doiList = model.publications.map(({ doi }) => doi);
  const intent = actions.hasChanges("publications") ? Intent.SUCCESS : null;

  if (isEditing) {
    return h("div", [
      h("h4", ["Publication DOI's"]),
      h(
        "div",
        {
          style: {
            display: "flex",
            flexDirection: "column",
          },
        },
        [
          doiList.map((doi, index) => {
            return h(
              "div",
              {
                display: "flex",
              },
              [
                h(DeleteButton, { index }),
                h(EditableText, {
                  mulitline: false,
                  onChange: (value) => onChangeHandler(index, value),
                  value: doi,
                  intent,
                }),
              ]
            );
          }),
        ]
      ),
    ]);
  }
  return h(ProjectPublications, { data: model.publications });
}

const EditNavBar = function(props) {
  return h(MinimalNavbar, { className: "project-editor-navbar" }, [
    h("h4", props.header),
    h(EditStatusButtons),
    h(EmbargoEditor),
  ]);
};

const EditableProjectDetails = function(props) {
  const { project, Edit } = props;
  const { login } = useAuth(); // this appears to be a boolean
  const { buildURL } = APIHelpers(useContext(APIContext));

  return h(
    ModelEditor,
    {
      model: project,
      canEdit: login || Edit,
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
        h("div", [Edit ? h(EditNavBar, { header: "Manage Project" }) : null]),
        h("div.project-editor-content", [
          h(ModelEditableText, { is: "h3", field: "name", multiline: true }),
          h(ModelEditableText, {
            is: "p",
            field: "description",
            multiline: true,
          }),
          h(EditablePublications),
        ]),
      ]),
    ]
  );
};

export { EditableProjectDetails, EditNavBar, ModelEditableText };
