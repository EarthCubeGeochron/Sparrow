/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from "react-hyperscript";
import styled from "@emotion/styled";
import { Component, useState } from "react";
import {
  Callout,
  Icon,
  Card,
  NonIdealState,
  Drawer,
  Button,
} from "@blueprintjs/core";
import {
  CollapsePanel,
  APIResultView,
  LinkCard,
} from "@macrostrat/ui-components";
import "./gdd-card.styl";

const Snippet = function({ html }) {
  const __html = html;
  console.log(__html);
  return h("p.snippet", { dangerouslySetInnerHTML: { __html } });
};

const SnippetResult = function(props) {
  const {
    title,
    pubname,
    publisher,
    coverDate,
    authors,
    highlight,
    URL,
  } = props;
  return h(
    LinkCard,
    { href: URL, target: "_blank", className: "snippet-result" },
    [
      h("h2.title", title),
      h("h3.authors", authors),
      h("h3.pub-info", [
        h("span.pubname", pubname),
        " — ",
        h("span.publisher", publisher),
      ]),
      h("h4.date", coverDate),
      h(
        "div.snippets",
        highlight.map((d) => h(Snippet, { html: d }))
      ),
    ]
  );
};

const SnippetList = (props) => {
  const { items } = props;
  if (items.length === 0) {
    return h(NonIdealState, {
      icon: "search",
      title: "No results found",
    });
  }
  return h(
    "div.snippet-list",
    null,
    items.map((d) => h(SnippetResult, d))
  );
};

const ResultsPanel = styled.div`\
display: flex;
flex-direction: row;
margin: 0 -0.5em;
&>div {
  margin: 0 0.5em;
}
.snippet-list {
  margin: 0.5em 0.5em;
}\
`;

const InfoCallout = styled(Callout)`\
width: 20em;\
`;

function GeoDeepDiveCard(props) {
  const [open, setOpen] = useState(false);

  const toggleOpen = () => {
    setOpen(!open);
  };

  const { sample_name } = props;
  const route = "https://geodeepdive.org/api/v1/snippets";
  const params = { term: sample_name };
  return (
    h(Button, { onClick: toggleOpen, text: "GeoDeepDive Search" }),
    h(
      Drawer,
      { isCloseButtonShown: true, onClose: toggleOpen },
      h(
        InfoCallout,
        {
          icon: "book",
          title: "Snippets containing sample name",
        },
        [
          h(
            "p",
            `The GeoDeepDive API can be used to aid \
the linking of sample names to their containing \
publications`
          ),
        ]
      ),
      h(APIResultView, { route, params }, (res) => {
        const {
          success: { data },
        } = res;
        return h(SnippetList, { items: data });
      })
    )
  );
}

export { GeoDeepDiveCard };
