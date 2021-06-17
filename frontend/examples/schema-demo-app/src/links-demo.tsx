import React, { useState } from "react";
import { Group } from "@visx/group";
import { hierarchy, Tree } from "@visx/hierarchy";
import { LinearGradient } from "@visx/gradient";
import { LinkHorizontal } from "@visx/shape";
import { pointRadial } from "d3-shape";
import useDimensions from "react-use-dimensions";
import h from "@macrostrat/hyper";
import { useDarkMode } from "@macrostrat/ui-components/src/dark-mode";
import { flextree } from "d3-flextree";
import classNames from "classnames";

function useForceUpdate() {
  const [, setValue] = useState<number>(0);
  return () => setValue((value) => value + 1); // update state to force render
}

interface TreeNode {
  name: string;
  isExpanded?: boolean;
  children?: TreeNode[];
}

const defaultMargin = { top: 30, left: 120, right: 120, bottom: 30 };

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
  console.log(link);
  return h(LinkHorizontal, {
    key: i,
    data: link,
    stroke: "#4af2a1",
    strokeWidth: 2,
    fill: "none",
  });
}

function SVGBackground({ totalWidth, totalHeight, children }: any) {
  const isEnabled = useDarkMode()?.isEnabled;
  let data = { from: "#eeeeee", to: "#fafafa" };
  if (isEnabled) data = { from: "#444444", to: "#333333" };
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

function NodeMembers({ node }) {
  const { members, group_by } = node.data?.term ?? {};
  if (members == null) return null;
  return h(
    "div.members",
    members.map((d) =>
      h("div.sub-term", [
        d.id ?? d,
        h.if(d.list ?? false)("span.modifier", [
          " (list",
          group_by == null ? "" : " by " + group_by,
          ")",
        ]),
      ])
    )
  );
}

function Node({ width, height, node, top, left }) {
  const schema = node.data.term?.members != null;
  const className = classNames({ schema });
  const forceUpdate = useForceUpdate();
  return h(
    "div.node",
    {
      style: {
        height,
        width,
        top,
        left,
        position: "absolute",
      },
      onClick: () => {
        node.data.isExpanded = !node.data.isExpanded;
        console.log(node);
        forceUpdate();
      },
    },
    h("div.node-content", { className }, [
      h("div.node-name", node.data.name),
      h(NodeMembers, { node }),
    ])
  );
}

export default function LinksArea({
  margin = defaultMargin,
  addGhostChild = false,
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
    let node = { name: term.id, term };
    if (term.members != null) {
      node.children = term.members.map((d) => {
        const name = d.id ?? d;
        const v = vocabMap[name];
        if (v != null) {
          childTerms.push(name);
          return createNode(v);
        } else {
          return createNode(d);
        }
      });
    } else {
      return { name: term.id };
    }
    return node;
  }

  const nestedNodes = vocabulary.terms.filter((d) => d != null).map(createNode);

  for (const node of nestedNodes) {
    const shouldRender = !childTerms.includes(node.name);
    if (shouldRender) {
      tree.children.push(node);
    }
  }

  const innerWidth = totalWidth - margin.left - margin.right;
  const innerHeight = totalHeight - margin.top - margin.bottom;
  const origin = { x: 0, y: 0 };
  const sizeWidth = innerHeight;
  const sizeHeight = innerWidth;

  if (totalWidth < 10) return null;

  const treeRoot = hierarchy(tree, (d) => d.children ?? []);
  //const treeRoot = hierarchy(data, (d) => (d.isExpanded ? null : d.children));

  // A flexible version
  // const layout = flextree().spacing(100);
  // let treeRoot = layout.hierarchy(tree);
  // layout(treeRoot);

  const nLevels = treeRoot.height - 1;

  const widthIncludingHiddenRoot = sizeHeight / (nLevels / (nLevels + 1));

  const renderTree = (tree) => {
    return h("div.tree-area", [
      h(
        SVGBackground,
        {
          totalWidth,
          totalHeight,
        },
        h(
          Group,
          {
            top: margin.top,
            left: margin.left + widthIncludingHiddenRoot,
          },
          h(
            Group,
            {
              top: origin.y,
              left: origin.x,
            },
            [tree.links().map(renderLink)]
          )
        )
      ),
      h(
        "div.tree-nodes",
        {
          style: {
            position: "absolute",
            top: 0,
            left: 0,
            width: totalWidth,
            height: totalHeight,
          },
        },
        tree.descendants().map((node) => {
          const width = 180;
          const height = 30;
          const top = node.x;
          const left = margin.left + widthIncludingHiddenRoot + node.y;
          if (node.depth === 0) return null;
          return h(Node, { width, height, node, top, left });
        })
      ),
    ]);
  };

  return h(
    "div.linker-ui-workspace",
    { ref },

    h(
      Tree,
      {
        root: treeRoot,
        size: [sizeWidth, -widthIncludingHiddenRoot],
        separation: (a, b) => {
          if (a.children != null && b.children != null) {
            return 5;
          } else if (a.children != null || b.children != null) {
            return 2;
          }
          return 1;
        },
      },
      renderTree
    )
  );
}
