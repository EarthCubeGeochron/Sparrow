import { hyperStyled } from "@macrostrat/hyper";
import { Card, Icon } from "@blueprintjs/core";
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
}
/**
 *
 * @param props : name (string), id (number), link (boolean), material (string), location_name? (string)
 */
const SampleCard = function(props: SampleCardProps) {
  let { material, id, name, location_name, link } = props;
  console.log(props);
  if (link == null) {
    link = true;
  }
  const component = link != null ? LinkCard : Card;
  const to = useModelURL(`/sample/${id}`);
  return h(component, { className: "sample-card", to }, [
    h("h4.name", name),
    h("div.location-name", location_name),
    h.if(material != null)("div.material", material),
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

export { SampleCard, AddSampleCard };
