import * as React from "react";
import h from "@macrostrat/hyper";
import { List } from "react-virtualized";
import { Button, Spinner, Card } from "@blueprintjs/core";
import { APIResultView } from "@macrostrat/ui-components/lib/types";
import { useAPIResult } from "../map/components/APIResult";
import styles from "../admin/sample/module.styl";
/** Left column of Sample Page. A virtualized list of buttons */

function getNames(data: []) {
  if (data !== null) {
    const list = [];
    data.forEach((sample) => {
      list.push(sample.name);
    });
    return list;
  } else {
    return null;
  }
}
function getMaterials(data: []) {
  if (data !== null) {
    const list = [];
    data.forEach((sample) => {
      list.push(sample.material);
    });
    return list;
  } else {
    return null;
  }
}

function getId(data: []) {
  if (data !== null) {
    const list = [];
    data.forEach((sample) => {
      list.push(sample.id);
    });
    return list;
  } else {
    return null;
  }
}

export function SampleList({ data, sendInfo }) {
  const [id, setId] = React.useState<number>();

  console.log(id);

  React.useEffect(() => {
    if (id !== null) {
      sendInfo(id);
    }
  }, [id]);

  const rowRenderer = ({ index, key }) => {
    if (data !== null) {
      const sampleNames = getNames(data);
      const ids = getId(data);
      const material = getMaterials(data);
      return h("div", [
        h(
          Card,
          {
            interactive: true,
            onClick: () => setId(ids[index]),
          },
          [
            h("h4", { key: ids[index], className: "sample-list-card" }, [
              "Sample: ",
              h("span.name", sampleNames[index]),
            ]),
            h.if(material != null)("div.material", material[index]),
          ]
        ),
      ]);
    }
  };

  return h(List, {
    width: 500,
    height: 1000,
    rowCount: 2017,
    rowHeight: 20,
    rowRenderer,
  });
}
