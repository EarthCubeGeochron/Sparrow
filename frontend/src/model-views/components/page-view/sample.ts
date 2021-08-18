import { hyperStyled } from "@macrostrat/hyper";
import { ModelLinkCard, PageViewBlock, PageViewDate } from "~/model-views";
import { DndChild } from "~/components";
import { useModelURL } from "~/util";
//@ts-ignore
import styles from "./module.styl";
import { useAPIv2Result } from "~/api-v2";
import { FormattedLngLat } from "./page-view";

const h = hyperStyled(styles);

export const SampleAdd = props => {
  const {
    onClickDelete = () => {},
    onClickList = () => {},
    data = [],
    draggable = true,
    setID = () => {},
    isEditing = false
  } = props;

  return h(
    PageViewBlock,
    {
      isEditing,
      modelLink: true,
      onClick: isEditing ? onClickList : null,
      model: "sample",
      title: "Samples",
      hasData: data.length != 0
    },
    h(PageViewSamples, {
      data,
      isEditing,
      draggable,
      onClick: onClickDelete,
      setID
    })
  );
};

export function PageViewSamples({
  data,
  isEditing,
  setID = () => {},
  link = true,
  onClick,
  draggable = true
}) {
  if (data == null) return null;
  return h(
    "div.sample-area",
    data.map(d => {
      const {
        material,
        id,
        name,
        location_name,
        session,
        location,
        linkedThrough
      } = d;
      return h(DndChild, { key: id, id, data: d, draggable }, [
        h(SampleCard, {
          key: id,
          material,
          session,
          id,
          location,
          name,
          location_name,
          setID,
          link,
          linkedThrough,
          onClick: () => onClick({ id, name }),
          isEditing
        })
      ]);
    })
  );
}

function SessionContent(props) {
  const { session } = props;

  if (session.length == 0) {
    return null;
  } else if (session.length > 1) {
    return h("div", [session.length, " Sessions"]);
  } else {
    return session.map((ele, i) => {
      return h.if(ele.date)("div", { key: i }, [
        h(PageViewDate, { date: ele.date }),
        ele.technique
      ]);
    });
  }
}

function Location(props) {
  const { location } = props;

  if (location == null) {
    return h("div", { style: { margin: 0 } });
  }
  const [longitude, latitude] = location.coordinates;

  return h(
    "h5.lon-lat",
    `[${Number(longitude).toFixed(3)} , ${Number(latitude).toFixed(3)}]`
  );
}

interface SampleCardProps {
  name: string;
  id: number;
  link: boolean;
  material: string;
  isEditing: boolean;
  session: any;
  location_name?: string;
  location?: any;
  setID?: (e) => void;
  onClick?: (e) => void;
}
/**
 *
 * @param props : name (string), id (number), link (boolean), material (string), location_name? (string)
 */
export function SampleCard(props: SampleCardProps) {
  let {
    material,
    id,
    name,
    location_name,
    location,
    link = true,
    setID,
    session = [],
    isEditing = false,
    onClick,
    ...rest
  } = props;

  const onHover = () => {
    //set id to state so marker is highlighted
    setID(id);
  };

  const onHoverLeave = () => {
    //Clear state so marker isn't highlighted
    setID(null);
  };

  const to = useModelURL(`/sample/${id}`);
  return h(
    ModelLinkCard,
    {
      draggable: false,
      className: "sample-card",
      to,
      isEditing,
      onMouseEnter: onHover,
      onMouseLeave: onHoverLeave,
      onClick,
      ...rest
    },
    [
      h("h4.name", name),
      h(FormattedLngLat, { location }),
      h.if(material != null)("div.material", material),
      h(SessionContent, { session })
    ]
  );
}

export function SubSamplePageView(props) {
  const { sample_id, isEditing } = props;

  let data = useAPIv2Result(
    `/models/sample/sub-sample/${sample_id}`,
    {},
    { unwrapResponse: data => data.sample_collection }
  );

  if (data == null) data = [];

  return h(
    PageViewBlock,
    {
      isEditing,
      title: "Sub-Samples",
      model: "sample",
      modelLink: true,
      hasData: data.length > 0
    },
    h(PageViewSamples, {
      data,
      isEditing,
      onClick: () => {},
      draggable: false
    })
  );
}
