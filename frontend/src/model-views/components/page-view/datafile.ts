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

import { PageViewBlock, PageViewModelCard, PageViewDate } from "~/model-views";
import { useModelURL } from "~/util";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

function DownloadButtonIcon(props) {
  const { basename, styles = {} } = props;

  if (basename.search(".xls") > 0) {
    return h(SiMicrosoftexcel, { style: { ...styles } });
  } else if (basename.search(".csv") > 0) {
    return h(GrDocumentCsv, { style: { ...styles } });
  } else if (basename.search(".bin") > 0) {
    return h(VscFileBinary, { style: { ...styles } });
  } else if (basename.search(".json") > 0) {
    return h(VscJson, { style: { ...styles } });
  } else if (basename.search(".xml") > 0) {
    return h(VscFileCode, { style: { ...styles } });
  } else if (basename.search(".txt") > 0) {
    return h(GrDocumentTxt, { style: { ...styles } });
  } else if (basename.search(".pdf") > 0) {
    return h(VscFilePdf, { style: { ...styles } });
  } else if (basename.search(".jpeg") > 0) {
    return h(VscFileMedia, { style: { ...styles } });
  } else if (basename.search(".png") > 0) {
    return h(VscFileMedia, { style: { ...styles } });
  } else if (basename.search(".jpg") > 0) {
    return h(VscFileMedia, { style: { ...styles } });
  } else if (basename.search(".tiff") > 0) {
    return h(VscFileMedia, { style: { ...styles } });
  }
  return h(AiFillFile, { style: { ...styles } });
}

function DownloadButtonContent(props) {
  const { file_hash, file_type, basename } = props;

  let text: any | React.ReactNode = "Data file";
  if (file_type != null) {
    text = h([h("b", { style: { marginLeft: "15px" } }, file_type)]);
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
        styles: { position: "absolute", bottom: "2px", left: "0" },
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
    h(
      AnchorButton,
      { href, rightIcon: "download", intent: Intent.PRIMARY, minimal: true },
      [h(DownloadButtonContent, { basename, file_hash, file_type })]
    ),
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
  const sample = useAPIv2Result(
    baseUrl + `?sample_id=${sample_ids}`,
    {},
    { unwrapResponse: unwrapDataFile }
  );
  const session = useAPIv2Result(
    baseUrl + `?session_id=${session_ids}`,
    {},
    { unwrapResponse: unwrapDataFile }
  );
  const analysis = useAPIv2Result(
    baseUrl + `?analysis_id=${analysis_ids}`,
    {},
    { unwrapResponse: unwrapDataFile }
  );
  if (analysis == null) return [];
  if (session == null) return [];
  if (sample == null) return [];

  return [...sample, ...session, ...analysis];
}

function DataFileCard(props) {
  const { date, basename, file_hash, model, current_model, model_id } = props;

  const content = h("div", [
    h("div", [h(PageViewDate, { date })]),
    h("div", [h("div", [h("h4", basename)])]),
  ]);

  const linkedThrough = h(
    "a",
    { href: useModelURL(`/${current_model}/${model_id}`) },
    [`${current_model} ${model_id}`]
  );

  if (current_model == model) {
    return h(
      PageViewModelCard,
      {
        link: true,
        to: useModelURL(`/data-file/${file_hash}`),
      },
      [content]
    );
  } else {
    return h(
      PageViewModelCard,
      {
        link: true,
        indirect: true,
        linkedThrough,
        styles: { maxWidth: "700px" },
        to: useModelURL(`/data-file/${file_hash}`),
      },
      [content]
    );
  }
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

export function DatafilePageView(props) {
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
      title: "Datafiles",
      hasData: true,
    },
    [h(DataFilePageCards, { data, model })]
  );
}
