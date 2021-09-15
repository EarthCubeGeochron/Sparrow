import { hyperStyled } from "@macrostrat/hyper";
import { useParams } from "react-router-dom";
import styles from "./module.styl";
import { DownloadButton, SampleAdd } from "~/model-views";
import { Divider, Spinner } from "@blueprintjs/core";
import { format } from "date-fns";
import { useModelEditor, ModelEditor } from "@macrostrat/ui-components";
import { useAuth } from "~/auth";
import { SampleCard } from "~/model-views";
import { Frame } from "~/frame";
import { useAPIv2Result } from "~/api-v2";
import {
  EditNavBar,
  ModelEditableText,
  SessionAdd,
  EmbargoDatePick,
  EditStatusButtons,
  ModelAttributeOneLiner,
  TagContainer,
  FormattedDate,
  PageViewBlock,
} from "../components";

const h = hyperStyled(styles);

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

const EditNavBarDataFile = () => {
  const { hasChanges, actions, isEditing, model } = useModelEditor();

  const onClickCancel = () => {
    actions.toggleEditing();
  };
  const onClickSubmit = () => {
    return actions.persistChanges();
  };

  return h(EditNavBar, {
    header: `Datafile ${model.basename}`,
    editButtons: h("div", { style: { display: "flex" } }, [
      // h(EditStatusButtons, {
      //   onClickCancel,
      //   onClickSubmit,
      //   hasChanges,
      //   isEditing
      // })
    ]),
  });
};

function getSample(link) {
  // We have a direct match
  if (link.sample != null) return link.sample;
  // We are linked through a session...
  if (link.session?.sample != null) {
    return {
      ...link.session.sample,
      linkedThrough: { model: "session", id: link.session.id },
    };
  }
  return null;
}

function DataFileSamples(props) {
  const { model } = useModelEditor();
  let samples = [];

  for (const link of model.data_file_link) {
    let sample = getSample(link);
    if (sample != null && !samples.find(({ id }) => id === sample.id)) {
      samples.push(sample);
    }
  }
  return h(SampleAdd, { isEditing: false, data: samples });
}

const DataFileSessions = (props) => {
  const { actions, isEditing, model } = useModelEditor();

  const sessions_links = model.data_file_link.filter(
    (obj) => obj.session != null
  );
  const sessions = sessions_links.map((obj) => {
    const session = obj.session;
    delete session.sample;

    return session;
  });

  return h(SessionAdd, { editable: false, data: sessions });
};

function DataFileDetails(props) {
  const { actions, isEditing, model } = useModelEditor();

  const lastModifiedDate = model.file_mtime;

  const dateUploaded = model.data_file_link[0]?.date;

  return h(PageViewBlock, [
    h(
      "div.data-file-header",
      { style: { display: "flex", justifyContent: "space-between" } },
      [
        h("div.main-content", [
          h("div.title-row.flex", [
            h("h3", { style: { margin: "0" } }, [model.basename]),
            h(DownloadButton, {
              file_type: model.type,
              file_hash: model.file_hash,
              basename: model.basename,
            }),
          ]),
          h(ModelAttributeOneLiner, {
            title: "Uploaded: ",
            content: h(FormattedDate, { date: dateUploaded }),
          }),
          h(ModelAttributeOneLiner, {
            title: "Last Modified: ",
            content: h(FormattedDate, { date: lastModifiedDate }),
          }),
          h(ModelAttributeOneLiner, {
            title: "Type: ",
            content: model.type,
          }),
        ]),
        h(Frame, { id: "dataFileHeaderExt", data: { dataFile: model } }, null),
      ]
    ),
  ]);
}

export function DataFilePage(props) {
  const { file_hash } = props;
  if (file_hash == null) return null;

  const dataFileURL = `/models/data_file/${file_hash}`;

  const res = useAPIv2Result(dataFileURL, {
    nest: "data_file_link,session,sample",
  });

  const { login } = useAuth();

  const data = res?.data;

  if (data == null) return h(Spinner);

  return h(
    ModelEditor,
    {
      model: data,
      canEdit: login,
    },
    [
      h("div.data-page-container", [
        h("div.header", [h.if(login)(EditNavBarDataFile)]),
        h("div.info-container", [
          h(DataFileDetails),
          h(DataFileSamples),
          h(DataFileSessions),
          h(Frame, { id: "dataFilePage", data }, null),
        ]),
      ]),
    ]
  );
}

export function DataFileMatch() {
  const { file_hash } = useParams();
  return h(DataFilePage, { file_hash });
}
