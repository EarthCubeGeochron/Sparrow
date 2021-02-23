import { useContext, useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  EditableText,
  Intent,
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
  ResearcherAdd,
  EditProjNewResearcher,
  PubAdd,
  EditProjNewPub,
  SampleAdd,
  EditProjNewSample,
} from "../new-model";
import { DatePicker } from "@blueprintjs/datetime";
import { APIV2Context } from "../../api-v2";
import { ProjectMap } from "./map";

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

  const onClickDelete = (id) => {
    const researchers = model.researchers == null ? [] : [...model.researchers];
    let newResearchers = [...researchers];
    const updatedRes = newResearchers.filter((ele) => ele.id != id);
    actions.updateState({
      model: { researchers: { $set: updatedRes } },
    });
  };

  const researchers = model.researchers == null ? [] : [...model.researchers];
  const names = researchers.map(({ name }) => name);
  console.log(names);

  return h(ResearcherAdd, {
    data: researchers,
    onClickDelete,
    onClickList: () => {
      console.log("researchers");
    },
    isEditing,
    rightElement: h(EditProjNewResearcher),
  });
}

/**
 * Component to display normal publication view, but on edit allow for the deletion, or addition of DOI's.
 * TODO: Have paper title appear, maybe in an alert or a tooltip, check to make sure it's the correct pub
 */
function EditablePublications(props) {
  const { isEditing, model, actions } = useModelEditor();
  console.log(model);

  if (model.publications == null && !isEditing) {
    return h("h4", ["No Publications"]);
  }

  const data = model.publications;

  const onClickDelete = (id) => {
    console.log(id);
  };

  return h(PubAdd, {
    data,
    onClickDelete,
    onClickList: () => {
      console.log("publications");
    },
    isEditing,
    rightElement: h(EditProjNewPub),
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

export function EditableSamples(props) {
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
  const onClickDelete = (id) => {
    console.log(id);
  };
  const onClickList = () => {
    console.log("samples");
  };

  return h(SampleAdd, {
    data: model.samples,
    setID,
    isEditing,
    onClickDelete,
    onClickList,
    rightElement: h(EditProjNewSample),
  });
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
