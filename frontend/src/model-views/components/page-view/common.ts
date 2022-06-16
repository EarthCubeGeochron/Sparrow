import { Tooltip, Card, Button } from "@blueprintjs/core";
import { format, getYear } from "date-fns";
import { useModelURL, useEditingAllowed } from "~/util";
import { ModelEditableText } from "~/model-views";
import { hyperStyled } from "@macrostrat/hyper";
import { LinkButton } from "@macrostrat/router-components";

//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const AddCard = (props) => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from existing ${model}s` },
    h(Button, { onClick, icon: "small-plus", minimal: true })
  );
};

export const NewModelButton = (props) => {
  const { model } = props;

  const to = useModelURL(`/${model}/new`);
  const handleClick = (e) => {
    e.preventDefault();
    window.location.href = to;
  };

  return h(
    LinkButton,
    {
      icon: "plus",
      minimal: true,
      intent: "success",
      to,
    },
    `New ${model}`
  );
};

export const ModelAttributeOneLiner = (props) => {
  const { title, content } = props;

  const displayContent = content ?? "None";

  return h("span", { style: { display: "flex", alignItems: "baseline" } }, [
    h("h4", { style: { marginRight: "4px" } }, title),
    " ",
    displayContent,
  ]);
};

export const PageViewBlock = (props) => {
  const {
    elevation = 1,
    title,
    children,
    isEditing = false,
    modelLink = false,
    onClick = () => {},
    hasData = true,
    model = "model",
  } = props;

  if (modelLink) {
    return h(
      Card,
      { elevation, style: { marginBottom: "15px", paddingTop: "0px" } },
      [
        h(
          "div",
          {
            style: { display: "flex", alignItems: "baseline", marginTop: "0" },
          },
          [
            h.if(title)("h3", [title]),
            h.if(isEditing)(AddCard, { onClick, model }),
          ]
        ),
        h.if(!hasData)("h4", `No ${model}s`),
        children,
      ]
    );
  }

  return h(Card, { elevation, style: { marginBottom: "15px" } }, [
    h.if(title)("h3", [title]),
    children,
  ]);
};

export const FormattedDate = (props) => {
  const { date, fallback = "Unknown date", oldestValidYear = 1940 } = props;

  const year = getYear(date);

  if (year < oldestValidYear) {
    if (fallback != null) {
      return h("div.formatted-date", null, "Unknown date");
    }
    return null;
  }
  return h("div.formatted-date", null, format(date, "MMMM D, YYYY"));
};

export const FormattedLngLat = (props) => {
  const { location, precision = 3 } = props;
  if (!location) return h("div");
  const { coordinates } = location;

  let [lng, lat] = coordinates;
  const fmtLng = lng.toFixed(precision);
  const fmtLat = lat.toFixed(precision);
  let lngString = lng > 0 ? `${fmtLng}° E` : `${fmtLng * -1}° W`;
  let latString = lat > 0 ? `${fmtLat}° N` : `${fmtLat * -1}° S`;

  return h("div.page-view-date", [`${lngString}, ${latString}`]);
};

export function ModelTitleBar(props): React.ReactNode {
  const {
    editingContent = null,
    rightContent = null,
    titleField = "name",
    subtitle,
  } = props;
  const isEditable = useEditingAllowed();

  // Set up the subtitle
  let subtitleElement = null;
  if (subtitle != null) {
    subtitleElement = h("h2.page-type", ["(", subtitle, ")"]);
  }

  return h("div.model-title-bar", [
    h(ModelEditableText, {
      is: "h2",
      field: titleField,
      multiline: false,
      placeholder: "Unnamed",
    }),
    subtitleElement,
    h("div.spacer"),
    h.if(isEditable)("div.page-type", null, editingContent),
    rightContent,
  ]);
}
