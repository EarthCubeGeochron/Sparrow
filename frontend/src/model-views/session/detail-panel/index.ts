/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import hyper from "@macrostrat/hyper";
import styles from "./module.styl";
import { Card, Breadcrumbs } from "@blueprintjs/core";
import { useAPIResult } from "@macrostrat/ui-components";
import ReactJson from "react-json-view";
import { format } from "d3-format";
import { group } from "d3-array";

const fmt = format(".3g");

const h = hyper.styled(styles);

const toTitleCase = function(str) {
  const func = txt => txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  return str.replace(/\w\S*/g, func);
};

const Material = function(props) {
  const { data } = props;
  if (data == null) {
    return null;
  }
  const items = data.reverse().map((d, i) => ({
    text: h("div", d),
    current: i === 0
  }));
  return h("div.material.datum", [
    h("h4", "Material"),
    h(Breadcrumbs, { items })
  ]);
};

function analysisAttributeUnwrap(data) {
  if (data == null || data.length === 0) {
    return [];
  }
  return group(data, d => d.parameter);
}

const AnalysisAttributes = function(props) {
  const { analysis_id } = props;
  const data = useAPIResult(
    "/attribute",
    { analysis_id },
    { unwrapResponse: analysisAttributeUnwrap }
  );
  if (!data || data.length == 0) {
    return h("div");
  }
  return h(
    Array.from(data, ([k, v]) =>
      h("li.attribute", [
        h("span.parameter", `${k}:`),
        h(
          "ul.values",
          v.map(d => h("li.value", d.value))
        )
      ])
    )
  );
};

const Unit = function({ unit }) {
  if (["unknown", "ratio"].includes(unit)) {
    return null;
  }
  return h("span.unit", unit);
};

const Datum = function(props) {
  const { value: d } = props;
  return h("li.datum.bp3-text", [
    h("span.parameter", `${d.parameter}:`),
    " ",
    h("span.value", fmt(d.value)),
    h.if(d.error != null)("span.error", [
      "±",
      h("span.error-value", fmt(d.error)),
      h.if(d.error_metric != null)("span.error-metric", `(${d.error_metric})`)
    ]),
    " ",
    h(Unit, { unit: d.unit })
  ]);
};

const DataCollection = function({ data, analysis_id }) {
  const datumList = h(data.map(d => h(Datum, { value: d })));

  return h("ul.data", [datumList, h(AnalysisAttributes, { analysis_id })]);
};

const AnalysisDetails = function(props) {
  const { data: a } = props;
  const { analysis_id } = a;

  if (a.analysis_id == null) {
    return h("h2", ["No analyses associated"]);
  }

  return h(Card, { className: "analysis-details" }, [
    h.if(a.analysis_type != null)(
      "h3.analysis-type",
      toTitleCase(a.analysis_type ?? "")
    ),
    h(Material, { data: a.material }),
    h("div.main", [
      h("div.data", [
        h("h4", "Data"),
        h(DataCollection, { data: a.data, analysis_id })
      ])
    ])
  ]);
};

const SessionDetails = function(props) {
  let { data, showTitle } = props;
  if (showTitle == null) {
    showTitle = false;
  }
  return h("div.session-details", [
    h.if(showTitle)("h2", "Analysis details"),
    data.map((d, i) => h(AnalysisDetails, { key: i, data: d }))
  ]);
};

const SessionDetailPanel = function(props) {
  const { session_id } = props;
  const data = useAPIResult("/analysis", { session_id });

  if (!data) return h("div");

  return h(SessionDetails, { data });
};

export { SessionDetailPanel };
