import * as React from "react";
import h from "@macrostrat/hyper";
import { useRouteMatch } from "react-router-dom";
import { useModelURL } from "~/util/router";
import { useAPIResult } from "@macrostrat/ui-components";
import { SampleListCard } from "../sample/list";

/**
 * http://localhost:5002/api/v2/models/data_file?nest=data_file_link,sample,session&per_page=100
 * Things to display on the data-files page
 *  Date of Upload to Sparrow
 *  Basename
 *  type
 *  Sample Link Cards,
 *  Project Link Cards,
 *  Session Link Cards,
 */

export function DataFilePage(props) {
  const {
    basename,
    type,
    date_upload,
    session_id,
    sample_name,
    sample_id,
    sample_material,
    project_name,
    project_id,
  } = props;
  return h("h1", ["Hello World"]);
}

const dataFileURL = "http://localhost:5002/api/v2/models/data_file";

// const DataFileComponent = function(props) {
//   const { file_hash } = props;
//   const data = useAPIResult(dataFileURL, {
//     id,
//   });
//   if (id == null || data == null) {
//     return null;
//   }

//   const data_file = data[0];
//   return h("div.data-view.project", null, h(DataFilePage, { data_file }));
// };

// export function DataFileMatch() {
//   const {
//     params: { id },
//   } = useRouteMatch();
//   return h(DataFileComponent, { id });
// }
