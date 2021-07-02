import { AnchorButton, Intent, Tooltip } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { SiMicrosoftexcel } from "react-icons/si";
import { AiFillFile } from "react-icons/ai";
import { GrDocumentCsv, GrDocumentTxt } from "react-icons/gr";
import {
  VscFileBinary,
  VscFilePdf,
  VscFileMedia,
  VscJson,
  VscFileCode
} from "react-icons/vsc";
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
        position: "relative"
      }
    },
    [
      h(DownloadButtonIcon, {
        basename,
        styles: { position: "absolute", bottom: "2px", left: "0" }
      }),
      text
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
    )
  ]);
}

export function DatafilePageView(props){
  
}