import { AnchorButton, Intent, Tooltip } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { APIV2Context, useAPIv2Result } from "~/api-v2";
import { SiMicrosoftexcel } from "react-icons/si";
import { AiFillFile } from "react-icons/ai";
import { GrDocumentCsv, GrDocumentTxt } from "react-icons/gr";
import { useAPIHelpers, buildQueryString } from "@macrostrat/ui-components";
import {
  VscFileBinary,
  VscFilePdf,
  VscFileMedia,
  VscJson,
  VscFileCode,
} from "react-icons/vsc";

import {
  PageViewBlock,
  ModelLinkCard,
  PageViewDate,
  LinkedThroughModel,
} from "~/model-views";
import { Frame } from "~/frame";
import { useModelURL } from "~/util";
//@ts-ignore
import styles from "./module.styl";
const h = hyperStyled(styles);

const iconIndex = {
  ".xls": SiMicrosoftexcel,
  ".csv": GrDocumentCsv,
  ".bin": VscFileBinary,
  ".json": VscJson,
  ".xml": VscFileCode,
  ".txt": GrDocumentTxt,
  ".pdf": VscFilePdf,
  ".jpeg": VscFileMedia,
  ".png": VscFileMedia,
  ".jpg": VscFileMedia,
  ".tiff": VscFileMedia,
};

function DownloadButtonIcon(props) {
  const { basename, style = {} } = props;
  for (const key in iconIndex) {
    if (basename.search(key) > 0) {
      return h(iconIndex[key], { style });
    }
  }
  return h(AiFillFile, { style });
}

function DownloadButtonContent(props) {
  const { file_hash, file_type, basename } = props;

  let text: any | React.ReactNode = "Download data file";
  if (file_type != null) {
    text = h(["Download ", h("b", file_type)]);
  }

  return h(
    "div",
    {
      style: {
        display: "flex",
        position: "relative",
      },
    },
    [
      text,
      " ",
      h(DownloadButtonIcon, {
        basename,
        style: {
          fontSize: "17px",
          marginLeft: "0.5em",
        },
      }),
    ]
  );
}

/**
 *
 * @param props : file_hash, type: as file_type
 */
export function DownloadButton(props) {
  const { file_hash, file_type, basename } = props;
  const { buildURL } = useAPIHelpers(APIV2Context);

  const href = buildURL(`/data_file/${file_hash}/download/`);
  return h(Tooltip, { content: `Download ${file_type ?? "data"} file` }, [
    h(AnchorButton, { href, intent: Intent.PRIMARY }, [
      h(DownloadButtonContent, { basename, file_hash, file_type }),
    ]),
  ]);
}

function unwrapDataFile(get_obj) {
  const { data, total_count } = get_obj;
  if (total_count == 0) return [];

  return data;
}

function useDataFileModelLinks(props) {
  const { sample_id, session_id, analysis_id } = props;

  const q = buildQueryString(
    { sample_id, session_id, analysis_id },
    { arrayFormat: "comma" }
  );

  const res = useAPIv2Result("/data_file/filter?" + q);
  console.log(res);
  return res?.data ?? [];
}

function DataFileCard(props) {
  const { date, basename, file_hash, model, current_model, model_id } = props;

  let linkedThrough: LinkedThroughModel | null = null;

  if (current_model != model) {
    linkedThrough = { model: current_model, id: model_id };
  }

  const dataFile = { date, basename, file_hash };

  return h(
    ModelLinkCard,
    {
      link: true,
      linkedThrough,
      to: useModelURL(`/data-file/${file_hash}`),
    },
    h(Frame, { id: "dataFileLinkContent", data: { dataFile } }, [
      h("div", [
        h("div", [h(PageViewDate, { date })]),
        h("div", [h("div", [h("h4", basename)])]),
      ]),
    ])
  );
}

function DataFilePageCards(props) {
  const { data, model } = props;
  if (data.length == 0) return h("div");

  return h("div", { style: { display: "flex", flexFlow: "row wrap" } }, [
    data.map((obj, i) => {
      const {
        basename,
        file_mtime: date,
        file_hash,
        model: current_model,
        model_id,
      } = obj;
      return h(DataFileCard, {
        basename,
        key: i,
        date,
        file_hash,
        model: model,
        current_model,
        model_id,
      });
    }),
  ]);
}

export function DataFilePage(props) {
  const { sample_ids = [], session_ids = [], analysis_ids = [], model } = props;

  const data = useDataFileModelLinks({
    sample_id: sample_ids,
    session_id: session_ids,
    analysis_id: analysis_ids,
  });
  return h(
    PageViewBlock,
    {
      model: "data_file",
      modelLink: true,
      title: "Data files",
      hasData: data.length > 0,
    },
    h(DataFilePageCards, { data, model })
  );
}
