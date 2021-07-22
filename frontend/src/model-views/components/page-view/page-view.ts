import { Tooltip, Card, Button } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import { format } from "date-fns";
import { useModelURL } from "~/util";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const AddCard = props => {
  const { onClick, model } = props;
  return h(
    Tooltip,
    { content: `Select from exisitng ${model}s` },
    h(Button, { onClick, icon: "small-plus", minimal: true })
  );
};

export const NewModelButton = props => {
  const { model } = props;

  const to = useModelURL(`/${model}/new`);
  const handleClick = e => {
    e.preventDefault();
    window.location.href = to;
  };

  const string = model.charAt(0).toUpperCase() + model.slice(1);

  return h(
    Button,
    {
      minimal: true,
      intent: "success",
      onClick: handleClick
    },
    [`New ${string}`]
  );
};

export const ModelAttributeOneLiner = props => {
  const { title, content } = props;

  let displayContent;
  if (!content) {
    displayContent = "None";
  } else {
    displayContent = content;
  }

  return h("span", { style: { display: "flex", alignItems: "baseline" } }, [
    h("h4", { style: { marginRight: "4px" } }, title),
    " ",
    displayContent
  ]);
};

export const PageViewBlock = props => {
  const {
    elevation = 1,
    title,
    children,
    isEditing = false,
    modelLink = false,
    onClick = () => {},
    hasData = true,
    model = "model"
  } = props;

  if (modelLink) {
    return h(
      Card,
      { elevation, style: { marginBottom: "15px", paddingTop: "0px" } },
      [
        h(
          "div",
          {
            style: { display: "flex", alignItems: "baseline", marginTop: "0" }
          },
          [
            h.if(title)("h3", [title]),
            h.if(isEditing)(AddCard, { onClick, model })
          ]
        ),
        h.if(!hasData)("h4", `No ${model}s`),
        children
      ]
    );
  }

  return h(Card, { elevation, style: { marginBottom: "15px" } }, [
    h.if(title)("h3", [title]),
    children
  ]);
};

export const PageViewDate = props => {
  const { date } = props;

  return h("div.page-view-date", [format(date, "MMMM D, YYYY")]);
};

export const PageViewLngLat = props => {
  const { location, precision = 3 } = props;
  if (!location) return h("div");
  const { coordinates } = location;

  let [lng, lat] = coordinates;

  let lngString =
    lng > 0
      ? `${lng.toFixed(precision)} E`
      : `${lng.toFixed(precision) * -1} W`;

  let latString =
    lat > 0
      ? `${lat.toFixed(precision)} N`
      : `${lat.toFixed(precision) * -1} S`;

  return h("div.page-view-date", [`${lngString}, ${latString}`]);
};
