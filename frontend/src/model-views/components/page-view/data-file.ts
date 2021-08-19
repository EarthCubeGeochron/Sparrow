import { AnchorButton, Intent, Tooltip } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useAPIv2Result } from "~/api-v2";
import { SiMicrosoftexcel } from "react-icons/si";
import { AiFillFile } from "react-icons/ai";
import { GrDocumentCsv, GrDocumentTxt } from "react-icons/gr";
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

  let text: any | React.ReactNode = "Data file";
  if (file_type != null) {
    text = h([
      h("b", { style: { fontSize: "17px", marginLeft: "22px" } }, file_type),
    ]);
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
      h(DownloadButtonIcon, {
        basename,
        style: {
          position: "absolute",
          bottom: "2px",
          left: "0",
          fontSize: "17px",
        },
      }),
      text,
    ]
  );
}

/**
 *
 * @param props : file_hash, type: as file_type
 */
export function DownloadButton(props) {
  const { file_hash, file_type, basename } = props;

  const href = `${process.env.BASE_URL}api/v2/data_file/${file_hash}`;
  return h(Tooltip, { content: `Download ${file_type} file` }, [
    h(AnchorButton, { href, rightIcon: "download", intent: Intent.PRIMARY }, [
      h(DownloadButtonContent, { basename, file_hash, file_type }),
    ]),
  ]);
}

function unwrapDataFile(get_obj) {
  const { data, total_count } = get_obj;
  if (total_count == 0) return [];

  return data;
}

function getDataFileData(props) {
  const { sample_ids = [0], session_ids = [0], analysis_ids = [0] } = props;

  const baseUrl = `/data_file/filter`;
  let sample = useAPIv2Result(
    baseUrl + `?sample_id=${sample_ids}`,
    {},
    { unwrapResponse: unwrapDataFile }
  );
  let session = useAPIv2Result(
    baseUrl + `?session_id=${session_ids}`,
    {},
    { unwrapResponse: unwrapDataFile }
  );
  let analysis = useAPIv2Result(
    baseUrl + `?analysis_id=${analysis_ids}`,
    {},
    { unwrapResponse: unwrapDataFile }
  );
  if (analysis == null) analysis = [];
  if (session == null) session = [];
  if (sample == null) sample = [];

  return [...sample, ...session, ...analysis];
}

function DataFileCard(props) {
  const { date, basename, file_hash, model, current_model, model_id } = props;

  let linkedThrough: LinkedThroughModel | null = null;

  if (current_model != model) {
    linkedThrough = { model: current_model, id: model_id };
  }

  return h(
    ModelLinkCard,
    {
      link: true,
      linkedThrough,
      to: useModelURL(`/data-file/${file_hash}`),
    },
    h("div", [
      h("div", [h(PageViewDate, { date })]),
      h("div", [h("div", [h("h4", basename)])]),
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
  const {
    sample_ids = [0],
    session_ids = [0],
    analysis_ids = [0],
    model,
  } = props;

  const data = getDataFileData({ sample_ids, session_ids, analysis_ids });
  return h(
    PageViewBlock,
    {
      model: "data_file",
      modelLink: true,
      title: "Data files",
      hasData: data.length > 0,
    },
    [h(DataFilePageCards, { data, model })]
  );
}
