import { useState, useEffect } from "react";
import { DataSheetSuggest } from "./datasheet-suggest";
import { useAPIResult } from "@macrostrat/ui-components";
import h from "@macrostrat/hyper";

const crossref = "https://api.crossref.org/v1/works/10.1130/b31239.1";

const doiURL = "https://xdd.wisc.edu/api/articles";

//This needs to be reworked into something else. This will not work.
export function DoiSuggest({
  defaultValue,
  onCellsChanged,
  onCommit,
  row,
  col,
  cell,
}) {
  const [input, setInput] = useState("");
  const [paperTitles, setPaperTitles] = useState([]);

  const paperData = useAPIResult(doiURL, { max: 10, title_like: input });

  useEffect(() => {
    if (paperData !== null) {
      try {
        const titles = paperData.success.data.map((paper) => paper.title);
        setPaperTitles(titles);
      } catch (error) {
        console.log(error);
        setPaperTitles([input]);
      }
    }
  }, [paperData]);

  const sendQuery = (query) => {
    setInput(query);
  };

  return h("div", [
    h(DataSheetSuggest, {
      items: paperTitles,
      defaultValue,
      onCellsChanged,
      onCommit,
      row,
      col,
      cell,
      sendQuery,
    }),
  ]);
}
