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
import {
  AddSampleControls,
  ProjectPublications,
  ProjectResearchers,
} from "./page";
import { DatePicker } from "@blueprintjs/datetime";
import { APIV2Context } from "../../api-v2";
import { ProjectMap } from "./map";
import { ProjectSamples } from "./page";

const h = hyperStyled(styles);

const ModelEditableText = function(props) {
  let {
    multiline,
    field,
    placeholder,
    is,
    editOn = false,
    onChange = () => {},
    value = null,
    ...rest
  } = props;
  const el = is || "div";
  if (placeholder == null) {
    placeholder = "Add a " + field;
  }
  delete rest.is;

  if (!editOn) {
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
  }
  const { id, onConfirm } = rest;
  return h(el, [
    h(EditableText, {
      className: "model-edit-text",
      multiline,
      placeholder,
      onChange,
      value,
      id,
      onConfirm,
    }),
  ]);
};

export const EmbargoDatePick = (props) => {
  const { onChange, embargo_date, active = true } = props;

  const text =
    embargo_date != null ? `Embargoed Until: ${embargo_date}` : "Public";
  const icon = embargo_date != null ? "lock" : "unlock";

  const Content = () => {
    return h(DatePicker, {
      minDate: new Date(),
      maxDate: new Date(2050, 1, 1),
      onChange: (e) => {
        let date = e.toISOString().split("T")[0];
        onChange(date);
      },
    });
  };

  return h("div.embargo-editor", [
    h(Popover, { content: h(Content), disabled: !active }, [
      h(Button, {
        text,
        minimal: true,
        interactive: false,
        rightIcon: icon,
        intent: Intent.SUCCESS,
        disabled: !active,
      }),
    ]),
  ]);
};

const EmbargoEditor = function(props) {
  const { model, actions, isEditing } = useContext(ModelEditorContext);
  const onChange = (date) => {
    actions.updateState({
      model: { embargo_date: { $set: date } },
    });
  };
  const embargo_date = model.embargo_date;

  return h(EmbargoDatePick, { onChange, embargo_date, active: isEditing });
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

function EditResearchers(props) {
  const { isEditing, model, actions } = useModelEditor();

  // update reasearcher by index of collection
  const onChangeHandler = (index, value) => {
    console.log(index);
    const researchers = model.researchers == null ? [] : [...model.researchers];
    let newResearchers = [...researchers];
    newResearchers[index] = { ...newResearchers[index], name: value };
    actions.updateState({
      model: { researchers: { $set: newResearchers } },
    });
  };

  const handleDelete = ({ index }) => {
    const researchers = model.researchers == null ? [] : [...model.researchers];
    let newResearchers = [...researchers];
    newResearchers.splice(index, 1);
    return actions.updateState({
      model: { researchers: { $set: newResearchers } },
    });
  };

  const handleAdd = () => {
    const researchers = model.researchers == null ? [] : [...model.researchers];
    let newResearchers = [...researchers];
    newResearchers.push({ name: "" });
    actions.updateState({
      model: { researchers: { $set: newResearchers } },
    });
  };

  const DeleteButton = (index) =>
    h(Button, {
      icon: "trash",
      intent: "danger",
      minimal: true,
      onClick: () => handleDelete(index),
    });

  const AddButton = () =>
    h(Button, {
      icon: "plus",
      intent: "success",
      minimal: true,
      onClick: handleAdd,
    });

  const researchers = model.researchers == null ? [] : [...model.researchers];
  const names = researchers.map(({ name }) => name);
  console.log(names);

  // if (isEditing) {
  //   return h("div", [
  //     h("h4", ["Project Researchers"]),
  //     names.length > 0
  //       ? h("div", [
  //           names.map((name, index) => {
  //             return h("div", [
  //               h(DeleteButton),
  //               h(EditableText, {
  //                 mulitline: false,
  //                 onChange: (value) => onChangeHandler(index, value),
  //                 value: name,
  //                 intent: "success",
  //                 placeholder: "Enter Researcher Name",
  //               }),
  //             ]);
  //           }),
  //           h(AddButton),
  //         ])
  //       : h(AddButton),
  //   ]);
  // }
  return h(ProjectResearchers, {
    data: researchers,
    isEditing,
    onClick: (id) => {
      console.log("Remove", id);
    },
  });
}

/**
 * Component to display normal publication view, but on edit allow for the deletion, or addition of DOI's.
 * TODO: Have paper title appear, maybe in an alert or a tooltip, check to make sure it's the correct pub
 */
function EditablePublications(props) {
  const { isEditing, model, actions } = useModelEditor();
  console.log(model);

  // use the index returned to locate the object in publications and update it.
  // replace the old publcations with a new array in the model
  const onChangeHandler = (index, value) => {
    let newPublications = [...model.publications];
    newPublications[index] = { ...newPublications[index], doi: value };
    actions.updateState({
      model: { publications: { $set: newPublications } },
    });
  };

  const handleDeletePub = ({ index }) => {
    let newPublications = [...model.publications];

    // this just gives the look
    newPublications.splice(index, 1);
    return actions.updateState({
      model: { publications: { $set: newPublications } },
    });
  };

  const handleAddPub = () => {
    let newPublications = [...model.publications];
    newPublications.push({ doi: "" });
    actions.updateState({
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

  //Need a plus button that will add an empty field where you can add a doi
  const AddButton = () =>
    h(Button, {
      icon: "plus",
      intent: "success",
      minimal: true,
      onClick: handleAddPub,
    });

  if (model.publications == null) {
    return h("h4", ["No Publications"]);
  }
  const doiList = model.publications.map(({ doi }) => doi);
  const intent = actions.hasChanges("publications") ? Intent.SUCCESS : null;

  // if (isEditing) {
  //   return h("div", [
  //     h("h4", ["Publication DOI's"]),
  //     h(
  //       "div",
  //       {
  //         style: {
  //           display: "flex",
  //           flexDirection: "column",
  //         },
  //       },
  //       [
  //         doiList.map((doi, index) => {
  //           return h(
  //             "div",
  //             {
  //               display: "flex",
  //               alignItems: "flex-start",
  //             },
  //             [
  //               h(DeleteButton, { index }),
  //               h(EditableText, {
  //                 mulitline: false,
  //                 onChange: (value) => onChangeHandler(index, value),
  //                 value: doi,
  //                 intent,
  //                 placeholder: "Enter DOI",
  //               }),
  //             ]
  //           );
  //         }),
  //         h(AddButton),
  //       ]
  //     ),
  //   ]);
  // }
  return h(ProjectPublications, {
    data: model.publications,
    isEditing,
    onClick: (id) => {
      console.log("Remove", id);
    },
  });
}

function SampleMapComponent() {
  const { model, actions, isEditing } = useModelEditor();

  const [hoverID, setHoverID] = useState();

  return h("div", [
    h("div", { style: { display: "flex", flexDirection: "row" } }, [
      h("div", { style: { paddingRight: "10px" } }, [
        h("h4", "Location"),
        h(ProjectMap, { samples: model.samples, hoverID }),
      ]),
      h(EditableSamples, { setID: setHoverID }),
    ]),
  ]);
}

function EditableSamples(props) {
  const { setID } = props;
  const { model, actions, isEditing } = useModelEditor();

  const handleDelete = ({ index }) => {
    let newSamples = [...model.samples];
    newSamples.splice(index, 1);
    return actions.updateState({
      model: { samples: { $set: newSamples } },
    });
  };
  const handleAdd = (samples) => {
    let newSamples = [...model.samples, ...samples];
    actions.updateState({
      model: { publications: { $set: newSamples } },
    });
  };

  if (isEditing) {
    return h("div", [
      h(ProjectSamples, {
        data: model.samples,
        setID,
        isEditing,
        onClick: () => {},
      }),
      h(AddSampleControls),
    ]);
  } else {
    return h(ProjectSamples, {
      data: model.samples,
      setID,
      isEditing: false,
      onClick: () => {},
    });
  }
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
  const { login } = useAuth();
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  return h(
    ModelEditor,
    {
      model: project,
      canEdit: login || Edit,
      persistChanges: async (updatedModel, changeset) => {
        let rest;
        let { id } = updatedModel;
        const response = await put(
          buildURL(`/models/project/${id}`, {}),
          changeset
        );
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
          h(EditResearchers),
          h(SampleMapComponent),
        ]),
      ]),
    ]
  );
};

export { EditableProjectDetails, EditNavBar, ModelEditableText };
