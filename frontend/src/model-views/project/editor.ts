import { useContext, useState, useEffect, createContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  EditableText,
  Intent,
  Button,
  Popover,
  ButtonGroup,
  Card,
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
import { MinimalNavbar, MySwitch } from "~/components";
import { put } from "axios";
import "../main.styl";
import styles from "~/admin/module.styl";
import {
  ResearcherAdd,
  EditProjNewResearcher,
  PubAdd,
  EditProjNewPub,
  SampleAdd,
  SessionAdd,
  EditProjNewSample,
} from "../new-model";
import { DatePicker } from "@blueprintjs/datetime";
import { APIV2Context } from "../../api-v2";
import { ProjectMap } from "./map";
import { ProjectAdminContext } from "~/admin/project";

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

const ToInfinityDate = (date) => {
  const newYear = date.getFullYear() + 3000;
  const month = date.getMonth();
  const day = date.getDay();
  return new Date(newYear, month, day);
};

export const EmbargoDatePick = (props) => {
  const { onChange, embargo_date, active = true } = props;
  // need to add an un-embargo if data is embargoed. And an infinite embargo

  let today = new Date();

  const embargoed = embargo_date && +embargo_date >= +today ? true : false;

  const infinite =
    embargo_date && embargo_date.getFullYear() === today.getFullYear() + 3000
      ? true
      : false;

  const text =
    embargo_date != null
      ? infinite
        ? "Embargoed Forever"
        : `Embargoed Until: ${embargo_date.toISOString().split("T")[0]}`
      : "Public";
  const icon = embargo_date != null ? "lock" : "unlock";

  console.log(embargoed);
  console.log(infinite);

  const Content = () => {
    return h(Card, [
      h(DatePicker, {
        minDate: new Date(),
        maxDate: new Date(2050, 1, 1),
        onChange: (e) => {
          let date = e.toISOString().split("T")[0];
          onChange(e);
        },
      }),
      h("div", [
        "Emargo Forever: ",
        h(MySwitch, {
          checked: infinite,
          onChange: () => onChange(ToInfinityDate(today)),
        }),
      ]),
      h.if(embargoed)("div", [
        "Make Data Public",
        h(MySwitch, { checked: !embargoed, onChange: () => onChange(null) }),
      ]),
    ]);
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

export const EmbargoEditor = function(props) {
  const { model, actions, isEditing } = useContext(ModelEditorContext);
  const onChange = (date) => {
    actions.updateState({
      model: { embargo_date: { $set: date } },
    });
  };
  const embargo_date = model.embargo_date;

  return h(EmbargoDatePick, { onChange, embargo_date, active: isEditing });
};

export const EditStatusButtons = function(props) {
  const { hasChanges, isEditing, onClickCancel, onClickSubmit } = props;

  const changed = hasChanges();
  return h("div.edit-status-controls", [
    h.if(!isEditing)(ModelEditButton, { minimal: true }, "Edit"),
    h.if(isEditing)(ButtonGroup, { minimal: true }, [
      h(
        SaveButton,
        {
          disabled: !changed,
          onClick: onClickSubmit,
        },
        "Save"
      ),
      h(
        CancelButton,
        {
          intent: changed ? "warning" : "none",
          onClick: onClickCancel,
        },
        "Done"
      ),
    ]),
  ]);
};

function EditStatusButtonsProj() {
  const { isEditing, hasChanges, actions } = useModelEditor();
  const { setListName } = useContext(ProjectAdminContext);

  const onClickCancel = () => {
    setListName("main");
    actions.toggleEditing();
  };

  const onClickSubmit = () => {
    setListName("main");
    return actions.persistChanges();
  };

  return h(EditStatusButtons, {
    onClickCancel,
    onClickSubmit,
    hasChanges,
    isEditing,
  });
}

function EditSessions(props) {
  const { isEditing, model, actions } = useModelEditor();
  const { setListName, changeFunction } = useContext(ProjectAdminContext);
  const { sampleHoverID } = useContext(SampleHoverIDContext);

  const addSession = (session_id, date, target, technique) => {
    const currentSessions = [...model.session];
    const newSess = new Array({ id: session_id, date, target, technique });
    const newSessions = [...currentSessions, ...newSess];
    actions.updateState({
      model: { session: { $set: newSessions } },
    });
  };

  const onClickDelete = ({ session_id: id, date }) => {
    console.log(id, date);
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

  useEffect(() => {
    changeFunction(addSession);
  }, [model.session]);

  const onDrop = (sample, session_id) => {
    // function that handles a sample drop into session container.
    // We want to add or replace the sample on the container session.
    // And then add the session to the sample
    const sess = [...model.session];
    const samp = [...model.sample];
    const { id: sample_id, name } = sample;
    console.log(sample_id, name); // this works
    const dropSession = sess.filter((ss) => ss.id == session_id);
    const otherSessions = sess.filter((ss) => ss.id != session_id);
    dropSession[0].sample = { id: sample_id, name };
    const newSess = [...dropSession, ...otherSessions];
    actions.updateState({
      model: { session: { $set: newSess } },
    });

    const [ss] = dropSession;
    const dragSample = samp.filter((sa) => sa.id == sample_id);
    const otherSamples = samp.filter((sa) => sa.id != sample_id);
    dragSample[0].session.push(ss);
    const newSamples = [...dragSample, ...otherSamples];
    actions.updateState({
      model: { sample: { $set: newSamples } },
    });
  };

  return h(SessionAdd, {
    data: model.session,
    sampleHoverID,
    isEditing,
    onClickList,
    onClickDelete,
    onDrop,
  });
}

function EditResearchers(props) {
  const { isEditing, model, actions } = useModelEditor();
  const { setListName, changeFunction } = useContext(ProjectAdminContext);

  const researchers = model.researcher == null ? [] : [...model.researcher];

  const onClickDelete = ({ id, name }) => {
    const updatedRes = researchers.filter((ele) => ele.name != name);
    actions.updateState({
      model: { researcher: { $set: updatedRes } },
    });
  };

  const onSubmit = (id, name) => {
    const newResearcher = new Array({ id, name });
    let newResearchers = [...researchers, ...newResearcher];
    actions.updateState({
      model: { researcher: { $set: newResearchers } },
    });
  };

  useEffect(() => {
    changeFunction(onSubmit);
  }, [model.researcher]);

  const names = researchers.map(({ name }) => name);

  return h(ResearcherAdd, {
    data: researchers,
    onClickDelete,
    onClickList: () => {
      changeFunction(onSubmit);
      setListName("researcher");
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

  if (model.publication == null && !isEditing) {
    return h("h4", ["No Publications"]);
  }
  const { setListName, changeFunction } = useContext(ProjectAdminContext);

  const data = model.publication == null ? [] : [...model.publication];

  const onClickDelete = ({ id, title }) => {
    const newPubs = data.filter((ele) => ele.title != title);
    actions.updateState({
      model: { publication: { $set: newPubs } },
    });
  };

  const onSubmit = (id, title, doi) => {
    const data = new Array({ id, title, doi });
    const publication = model.publication == null ? [] : [...model.publication];
    let newPubs = [...publication, ...data];
    actions.updateState({
      model: { publication: { $set: newPubs } },
    });
  };

  useEffect(() => {
    changeFunction(onSubmit);
  }, [model.publication]);

  return h(PubAdd, {
    data,
    onClickDelete,
    onClickList: () => {
      changeFunction(onSubmit);
      setListName("publication");
    },
    isEditing,
    rightElement: h(EditProjNewPub),
  });
}

function SampleMapComponent() {
  const { model, actions, isEditing } = useModelEditor();
  const { sampleHoverID } = useContext(SampleHoverIDContext);

  return h("div", [
    h("div", { style: { display: "flex", flexDirection: "row" } }, [
      h("div", { style: { paddingRight: "10px" } }, [
        h("h4", "Location"),
        h(ProjectMap, { samples: model.sample, hoverID: sampleHoverID }),
      ]),
      h(EditableSamples),
    ]),
  ]);
}

export function EditableSamples() {
  const { setHoverID } = useContext(SampleHoverIDContext);
  const { model, actions, isEditing } = useModelEditor();
  const { setListName, changeFunction } = useContext(ProjectAdminContext);

  const samples =
    model.sample == null || model.sample == [] ? [] : [...model.sample];

  const onClickDelete = ({ id, name }) => {
    const newSamples = id
      ? samples.filter((ele) => ele.id != id)
      : samples.filter((ele) => ele.name != name);
    return actions.updateState({
      model: { sample: { $set: newSamples } },
    });
  };

  const sampleOnClick = (id, name) => {
    const newSample = new Array({ id, name });
    let newSamples = [...samples, ...newSample];
    return actions.updateState({
      model: { sample: { $set: newSamples } },
    });
  };

  useEffect(() => {
    changeFunction(sampleOnClick);
  }, [model.sample]);

  const onClickList = () => {
    changeFunction(sampleOnClick);
    setListName("sample");
  };

  return h(SampleAdd, {
    data: model.sample,
    setID: setHoverID,
    isEditing,
    onClickDelete,
    onClickList,
    rightElement: h(EditProjNewSample),
  });
}

const EditNavBar = function(props) {
  const { editButtons, embargoEditor, header } = props;
  return h(MinimalNavbar, { className: "project-editor-navbar" }, [
    h("h4", header),
    editButtons,
    embargoEditor,
  ]);
};

const ProjEditNavBar = ({ header }) => {
  return h(EditNavBar, {
    header,
    editButtons: h(EditStatusButtonsProj),
    embargoEditor: h(EmbargoEditor),
  });
};

const SampleHoverIDContext = createContext({});

const EditableProjectDetails = function(props) {
  const { project, Edit } = props;
  const { login } = useAuth();
  const { buildURL } = APIHelpers(useContext(APIV2Context));

  const [sampleHoverID, setSampleHoverID] = useState();

  const setHoverID = (id) => {
    setSampleHoverID(id);
  };

  return h(
    ModelEditor,
    {
      model: project.data,
      canEdit: login || Edit,
      persistChanges: async (updatedModel, changeset) => {
        console.log(changeset);
        console.log(updatedModel);
        let rest;
        let { id } = updatedModel;
        const response = await put(
          buildURL(`/project/edit/${id}`, {}),
          updatedModel
        );
        const { data } = response;
        ({ id, ...rest } = data);
        return rest;
      },
    },
    [
      h(
        SampleHoverIDContext.Provider,
        { value: { sampleHoverID, setHoverID } },
        [
          h("div.project-editor", [
            h("div", [
              Edit ? h(ProjEditNavBar, { header: "Manage Project" }) : null,
            ]),
            h("div.project-editor-content", [
              h(ModelEditableText, {
                is: "h3",
                field: "name",
                multiline: true,
              }),
              h(ModelEditableText, {
                is: "p",
                field: "description",
                multiline: true,
              }),
              h(EditablePublications),
              h(EditResearchers),
              h(EditSessions),
              h(SampleMapComponent),
            ]),
          ]),
        ]
      ),
    ]
  );
};

export { EditableProjectDetails, EditNavBar, ModelEditableText };
