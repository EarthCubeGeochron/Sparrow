import { useContext, useState, useEffect, createContext } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import { useAuth } from "~/auth";
import {
  ModelEditor,
  ModelEditorContext,
  useModelEditor,
  APIHelpers,
} from "@macrostrat/ui-components";
import { put } from "axios";
import "../main.styl";
import styles from "~/admin/module.styl";
import {
  ResearcherAdd,
  PubAdd,
  SampleAdd,
  SessionAdd,
  ModelEditableText,
  EmbargoDatePick,
  EditStatusButtons,
  EditNavBar,
} from "../components";
import { APIV2Context } from "../../api-v2";
import { ProjectMap } from "./map";
import { ProjectAdminContext } from "~/admin/project";
import { Frame } from "~/frame";

const h = hyperStyled(styles);

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
    if (isEditing) {
      changeFunction(addSession);
    }
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

  const onSubmit = (id, name, orcid = null) => {
    const newResearcher = new Array({ id, name, orcid });
    let newResearchers = [...researchers, ...newResearcher];
    actions.updateState({
      model: { researcher: { $set: newResearchers } },
    });
  };

  useEffect(() => {
    if (isEditing) {
      changeFunction(onSubmit);
    }
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
    if (isEditing) {
      changeFunction(onSubmit);
    }
  }, [model.publication]);

  return h(PubAdd, {
    data,
    onClickDelete,
    onClickList: () => {
      changeFunction(onSubmit);
      setListName("publication");
    },
    isEditing,
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

  const sampleOnClick = (sample) => {
    const newSample = new Array(sample);
    let newSamples = [...samples, ...newSample];
    return actions.updateState({
      model: { sample: { $set: newSamples } },
    });
  };

  useEffect(() => {
    if (isEditing) {
      changeFunction(sampleOnClick);
    }
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
  });
}

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

  console.log(project.data);

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
        console.log(data);
        ({ data } = data);
        return data;
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
              h(Frame, { id: "projectPage", data: project.data }, null),
            ]),
          ]),
        ]
      ),
    ]
  );
};

export { EditableProjectDetails };
