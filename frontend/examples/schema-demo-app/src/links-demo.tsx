import React, { useState } from "react";
import { Group } from "@visx/group";
import { hierarchy, Tree } from "@visx/hierarchy";
import { LinearGradient } from "@visx/gradient";
import { LinkHorizontal } from "@visx/shape";
import { pointRadial } from "d3-shape";
import useDimensions from "react-use-dimensions";
import h from "@macrostrat/hyper";
import { useDarkMode } from "@macrostrat/ui-components/src/dark-mode";

function useForceUpdate() {
  const [, setValue] = useState<number>(0);
  return () => setValue((value) => value + 1); // update state to force render
}

interface TreeNode {
  name: string;
  isExpanded?: boolean;
  children?: TreeNode[];
}

const data: TreeNode = {
  name: "hidden_root",
  children: [
    {
      name: "Concordia parameters",
      children: [
        { name: "Error correlation" },
        { name: "206Pb/238U ratio" },
        { name: "207Pb/238U ratio" },
        {
          name: "C",
          children: [
            {
              name: "C1",
            },
            {
              name: "D",
              children: [
                {
                  name: "D1",
                },
                {
                  name: "D2",
                },
                {
                  name: "D3",
                },
              ],
            },
          ],
        },
      ],
    },
    { name: "Z" },
    {
      name: "B",
      children: [{ name: "B1" }, { name: "B2" }, { name: "B3" }],
    },
  ],
};

const defaultMargin = { top: 30, left: 70, right: 70, bottom: 30 };

export type LinkTypesProps = {
  width: number;
  height: number;
  margin?: { top: number; right: number; bottom: number; left: number };
  vocabulary: {
    terms: any[];
  };
};

function renderLink(link, i) {
  if (link.source.data.name == "hidden_root") return null;
  return h(LinkHorizontal, {
    key: i,
    data: link,
    stroke: "#4af2a1",
    strokeWidth: 2,
    fill: "none",
  });
}

function Background({ totalWidth, totalHeight, children }) {
  const inDarkMode = useDarkMode();
  let data = { from: "#cccccc", to: "#dddddd" };
  if (inDarkMode) data = { from: "#444444", to: "#333333" };
  return h("svg", { width: totalWidth, height: totalHeight }, [
    h(LinearGradient, { id: "links-gradient", ...data }),
    h("rect", {
      width: totalWidth,
      height: totalHeight,
      rx: 14,
      fill: data.to,
    }),
    children,
  ]);
}

function Node({ width, height, node }) {
  const forceUpdate = useForceUpdate();
  return h("rect", {
    height: height,
    width: width,
    y: -height / 2,
    x: -width / 2,
    fill: "#ffffff",
    stroke: "#888888",
    strokeWidth: 1,
    strokeDasharray: node.data.children ? "0" : "2,2",
    strokeOpacity: node.data.children ? 1 : 0.6,
    rx: node.data.children ? 0 : 4,
    onClick: () => {
      node.data.isExpanded = !node.data.isExpanded;
      console.log(node);
      forceUpdate();
    },
  });
}

function renderNodes(node, key) {
  const width = 80;
  const height = 30;
  let top = node.x;
  let left = node.y;
  if (node.depth === 0) return null;
  return h(
    Group,
    {
      top: top,
      left: left,
      key: key,
    },
    [
      h(Node, { width, height, node }),
      h(
        "text",
        {
          dy: ".33em",
          fontSize: 9,
          fontFamily: "Arial",
          textAnchor: "middle",
          style: {
            pointerEvents: "none",
          },
          fill: "black",
        },
        node.data.name
      ),
    ]
  );
}

export default function LinksArea({
  margin = defaultMargin,
  vocabulary,
}: LinkTypesProps) {
  const [ref, { width: totalWidth, height: totalHeight }] = useDimensions();

  var vocabMap = vocabulary.terms.reduce(function (map, node) {
    map[node.id] = node;
    return map;
  }, {});

  let tree: TreeNode = {
    name: "hidden_root",
    children: [],
  };

  let childTerms: string[] = [];

  function createNode(term) {
    console.log(term);
    let node = { name: term.id, term };
    if (term.members != null) {
      node.children = term.members.map((d) => {
        const name = d.id ?? d;
        const v = vocabMap[name];
        if (v != null) {
          childTerms.push(name);
          return createNode(v);
        } else {
          return { name, ghost: true };
        }
      });
    }
    return node;
  }

  const nestedNodes = vocabulary.terms.filter((d) => d != null).map(createNode);

  for (const node of nestedNodes) {
    if (!childTerms.includes(node.name)) {
      tree.children.push(node);
    }
  }

  const innerWidth = totalWidth - margin.left - margin.right;
  const innerHeight = totalHeight - margin.top - margin.bottom;
  const origin = { x: 0, y: 0 };
  const sizeWidth = innerHeight;
  const sizeHeight = innerWidth;

  if (totalWidth < 10) return null;

  const treeRoot1 = hierarchy(data, (d) => d.children ?? []);
  const treeRoot = hierarchy(tree, (d) => d.children ?? []);
  console.log(tree, treeRoot, treeRoot1);
  //const treeRoot = hierarchy(data, (d) => (d.isExpanded ? null : d.children));
  const nLevels = treeRoot.height - 1;

  const widthIncludingHiddenRoot = sizeHeight / (nLevels / (nLevels + 1));

  return (
    <div className="linker-ui-workspace" ref={ref}>
      <Background totalWidth={totalWidth} totalHeight={totalHeight}>
        <Group top={margin.top} left={margin.left + widthIncludingHiddenRoot}>
          <Tree
            root={treeRoot}
            size={[sizeWidth, -widthIncludingHiddenRoot]}
            separation={(a, b) => (a.parent === b.parent ? 0.2 : 0.5) / a.depth}
          >
            {(tree) => {
              return h(Group, { top: origin.y, left: origin.x }, [
                tree.links().map(renderLink),
                tree.descendants().map(renderNodes),
              ]);
            }}
          </Tree>
        </Group>
      </Background>
    </div>
  );
}
