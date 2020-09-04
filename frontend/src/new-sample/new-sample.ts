import * as React from "react";
import h from "@macrostrat/hyper";
import { SampleFilter } from "../filter";
import { SampleList } from "./sample-list";
import { useAPIResult } from "../map/components/APIResult";
import SampleInfo from "./sample-info";
import styles from "./sample-page.module.css";

/** Rough Drafting for the new ui's sample page */

function NewSample() {
  const intialState = useAPIResult<[]>("/sample", { all: true });

  const [state, setState] = React.useState({
    List: [],
    Info: {},
  });

  React.useEffect(() => {
    if (intialState !== null) {
      setState({ ...state, List: intialState });
    }
  }, [intialState]);
  console.log(state);

  // This function will provide the right column with the data for the sample that was clicked
  function infoFromClick(id) {
    state.List.forEach((sample) => {
      if (id === sample.id) {
        setState({ ...state, Info: sample });
      }
    });
    //setState({ ...state, Info: clickedSample });
  }

  return h("div", [
    h("h1", ["Welcome to the New Sample Page"]),
    h(SampleFilter),
    h("div", { className: styles.row }, [
      h("div", { className: styles.column }, [
        h(SampleList, {
          data: state.List,
          sendInfo: infoFromClick,
        }),
      ]),
      h("div", { className: styles.column }, [
        h(SampleInfo, { data: state.Info }),
      ]),
    ]),
  ]);
}

export default NewSample;
