import { hyperStyled } from "@macrostrat/hyper";
import { Card, Icon, Button, ButtonGroup } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import style from "./card.module.css";
import styles from "./module.styl";
import { useModelURL } from "~/util/router";

const h = hyperStyled(styles);

interface SampleCardProps {
  name: string;
  id: number;
  link: boolean;
  material: string;
  location_name?: string;
  setID?: (any) => {};
  onClick?: (any) => {};
}
/**
 *
 * @param props : name (string), id (number), link (boolean), material (string), location_name? (string)
 */
const SampleCard = function(props: SampleCardProps) {
  let { material, id, name, location_name, link = true, setID } = props;

  const onHover = () => {
    //set id to state so marker is highlighted
    setID(id);
  };

  const onHoverLeave = () => {
    //Clear state so marker isn't highlighted
    setID(null);
  };

  const component = link ? LinkCard : Card;
  const to = useModelURL(`/sample/${id}`);
  return h(
    component,
    {
      className: "sample-card",
      to,
      onMouseEnter: onHover,
      onMouseLeave: onHoverLeave,
    },
    [
      h("h4.name", name),
      h("div.location-name", location_name),
      h.if(material != null)("div.material", material),
    ]
  );
};

/**
 * Component to allow for deletion of samples from Project.
 * @param props
 */
const SampleEditCard = (props) => {
  let { id, name, onClick } = props;

  return h("div.sample-edit-card", [
    h("h4.name", name),
    h(Button, {
      minimal: true,
      icon: "trash",
      intent: "danger",
      onClick: () => onClick(id),
    }),
  ]);
};

const PubEditCard = (props) => {
  let { id, content, onClick } = props;

  return h("div.pub-edit-card", [
    content,
    h(Button, {
      minimal: true,
      icon: "trash",
      intent: "danger",
      onClick: () => onClick(id),
    }),
  ]);
};

const ResearcherEditCard = (props) => {
  let { id, name, onClick } = props;

  return h("div.sample-edit-card", [
    h("h4.name", name),
    h(Button, {
      minimal: true,
      icon: "trash",
      intent: "danger",
      onClick: () => onClick(id),
    }),
  ]);
};

interface AddSample {
  icon_name: string;
  onClick: () => {};
}

const AddSampleCard = (props: AddSample) => {
  const { onClick, icon_name } = props;
  return h("div", { className: style.addSample, onClick }, ["+"]);
};

export {
  SampleCard,
  AddSampleCard,
  SampleEditCard,
  PubEditCard,
  ResearcherEditCard,
};
