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
import { useAPIv3Result } from "~/api-v2";
import ReactJson from "react-json-view";
import { format } from "d3-format";
import { group } from "d3-array";

const fmt = format(".3g");

const h = hyper.styled(styles);

const toTitleCase = function (str) {
  const func = (txt) =>
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  return str.replace(/\w\S*/g, func);
};

const Material = function (props) {
  const { data } = props;
  if (data == null) {
    return null;
  }
  const items = data.reverse().map((d, i) => ({
    text: h("div", d),
    current: i === 0,
  }));
  return h("div.material.datum", [
    h("h4", "Material"),
    h(Breadcrumbs, { items }),
  ]);
};

const AnalysisAttributes = function (props) {
  const { attributes = [] } = props;
  const data = group(attributes, (d) => d.parameter);

  return h(
    Array.from(data, ([k, v]) =>
      h("li.attribute", [
        h("span.parameter", `${k}:`),
        h(
          "ul.values",
          v.map((d) => h("li.value", d.value))
        ),
      ])
    )
  );
};

const Unit = function ({ unit }) {
  if (["unknown", "ratio", "dimensionless"].includes(unit)) {
    return null;
  }
  return h("span.unit", unit);
};

const Datum = function (props) {
  const { value: d } = props;
  return h("li.datum.bp4-text", [
    h("span.parameter", `${d.parameter}:`),
    " ",
    h("span.value", fmt(d.value)),
    h.if(d.error != null)("span.error", [
      "±",
      h("span.error-value", fmt(d.error)),
      h.if(d.error_metric != null)("span.error-metric", `(${d.error_metric})`),
    ]),
    " ",
    h(Unit, { unit: d.unit }),
  ]);
};

const DataCollection = function ({ data, attributes }) {
  if (data == null) return null;
  const datumList = h(data.map((d) => h(Datum, { value: d })));
  return h("ul.data", [datumList, h(AnalysisAttributes, { attributes })]);
};

const AnalysisDetails = function (props) {
  const { data: a } = props;
  const { analysis_id } = a;

  if (a.analysis_id == null) {
    return h("h3", ["No analyses associated"]);
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
        h(DataCollection, {
          data: a.data,
          attributes: a.attributes ?? [],
        }),
      ]),
    ]),
  ]);
};

const SessionDetails = function (props) {
  let { data, showTitle = false } = props;
  return h("div.session-details", [
    h.if(showTitle)("h2", "Analysis details"),
    data.map((d, i) => h(AnalysisDetails, { key: i, data: d })),
  ]);
};

function SessionDetailPanel(props) {
  const { session_id, ...rest } = props;
  const data = useAPIv3Result("/analysis", {
    session_id: `eq.${session_id}`,
  });

  if (!data) return h("div");

  return h(SessionDetails, { data, ...rest });
}

export { SessionDetailPanel };
