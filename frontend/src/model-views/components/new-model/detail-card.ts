import { hyperStyled } from "@macrostrat/hyper";
import { Card, Icon, Button, ButtonGroup } from "@blueprintjs/core";
import { LinkCard } from "@macrostrat/ui-components";
//@ts-ignore
import style from "./card.module.css"; // I know this looks repitative, but don't delete yet please
//@ts-ignore
import styles from "./module.styl";
import { useModelURL } from "~/util/router";

const h = hyperStyled(styles);

interface SampleCardProps {
  name: string;
  id: number;
  link: boolean;
  material: string;
  session: any;
  location_name?: string;
  setID?: (e) => void;
  onClick?: (e) => void;
}
/**
 *
 * @param props : name (string), id (number), link (boolean), material (string), location_name? (string)
 */
const SampleCard = function(props: SampleCardProps) {
  let {
    material,
    id,
    name,
    location_name,
    link = true,
    setID,
    session = [],
  } = props;

  const onHover = () => {
    //set id to state so marker is highlighted
    setID(id);
  };

  const onHoverLeave = () => {
    //Clear state so marker isn't highlighted
    setID(null);
  };

  const sessionContent = h.if(session.length > 0)("div", [
    session.map((ele) => {
      return h.if(ele.date)("div", [
        ele.date.split("T")[0],
        ",     ",
        ele.target,
      ]);
    }),
  ]);

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
      sessionContent,
    ]
  );
};

/**
 * Component to allow for deletion of samples from Project.
 * @param props
 */
const SampleEditCard = (props) => {
  const { id, name, onClick, session = [], setID = () => {} } = props;

  const sessionContent = h.if(session.length > 0)("div", [
    session.map((ele) => {
      return h.if(ele.date)("div", [
        ele.date.split("T")[0],
        ",     ",
        ele.target,
      ]);
    }),
  ]);

  return h(
    "div.sample-edit-card",
    { onMouseEnter: () => setID(id), onMouseLeave: () => setID(null) },
    [
      h("div", [h("h4.name", name), sessionContent]),
      h(Button, {
        key: name,
        minimal: true,
        icon: "trash",
        intent: "danger",
        onClick: () => onClick({ id, name }),
      }),
    ]
  );
};

const PubEditCard = (props) => {
  let { id, title, content, onClick } = props;

  return h("div.pub-edit-card", [
    content,
    h(Button, {
      minimal: true,
      icon: "trash",
      intent: "danger",
      onClick: () => onClick({ id, title }),
    }),
  ]);
};

const ResearcherEditCard = (props) => {
  let { id, name, onClick } = props;

  return h("div.sample-edit-card", [
    h("h4.name", name),
    h(Button, {
      id: id,
      minimal: true,
      icon: "trash",
      intent: "danger",
      onClick: () => onClick({ id, name }),
    }),
  ]);
};

export const ProjectEditCard = (props) => {
  const { d, onClick } = props;
  const project = d.project.map((obj) => {
    if (obj) {
      const { name, id } = obj;
      return { name, id };
    }
    return null;
  });

  return h("div", [
    project.map((obj) => {
      if (!obj) return null;
      const { name, id } = obj;
      return h("div.sample-edit-card", [
        h("h4.name", name),
        h(Button, {
          id: id,
          minimal: true,
          icon: "trash",
          intent: "danger",
          onClick: () => onClick({ id, name }),
        }),
      ]);
    }),
  ]);
};

export const SessionEditCard = (props) => {
  const {
    onClick,
    session_id,
    target,
    date,
    technique,
    sample = null,
    onHover = false,
  } = props;

  const classname = onHover ? "sample-edit-card-samhover" : "sample-edit-card";

  const sampleName = sample ? sample.name : "";

  return h(`div.${classname}`, [
    h("div.session-info", [
      h("div", [date.split("T")[0], ",     ", target]),
      h("div", technique),
      h.if(sample)("div", [h("i", `Linked through ${sampleName}`)]),
    ]),
    h(Button, {
      id: session_id,
      minimal: true,
      icon: "trash",
      intent: "danger",
      onClick: () => onClick({ session_id, date }),
    }),
  ]);
};

interface AddSample {
  icon_name: string;
  onClick: () => {};
}

const AddSampleCard = (props: AddSample) => {
  const { onClick } = props;
  return h("div", { className: style.addSample, onClick }, ["+"]);
};

export {
  SampleCard,
  AddSampleCard,
  SampleEditCard,
  PubEditCard,
  ResearcherEditCard,
};
