import { hyperStyled } from "@macrostrat/hyper";
import { Card } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
import styles from "./module.styl";

const h = hyperStyled(styles);

interface SampleCardProps {
  name: string;
  id: number;
  link: boolean;
  material: string;
  location_name?: string;
}

const SampleCard = function (props: SampleCardProps) {
  let { material, id, name, location_name, link } = props;
  console.log(props);
  if (link == null) {
    link = true;
  }
  const component = link != null ? LinkCard : Card;
  const to = `/catalog/sample/${id}`;
  return h(component, { className: "sample-card", to }, [
    h("h4.name", name),
    h("div.location-name", location_name),
    h.if(material != null)("div.material", material),
  ]);
};

export { SampleCard };
