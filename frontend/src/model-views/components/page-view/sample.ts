import { hyperStyled } from "@macrostrat/hyper";
import styled from "@emotion/styled";
import { PageViewModelCard, PageViewBlock, PageViewDate } from "../index";
import { DndChild } from "~/components";
import { useModelURL } from "~/util";
//@ts-ignore
import styles from "./module.styl";
import { useAPIv2Result } from "~/api-v2";

const h = hyperStyled(styles);

export const SampleAdd = (props) => {
  const {
    onClickDelete = () => {},
    onClickList = () => {},
    data,
    draggable = true,
    isEditing = true,
    setID = () => {},
    editable = true,
  } = props;

  if (!editable) {
    return h(
      PageViewBlock,
      {
        isEditing: false,
        modelLink: true,
        model: "sample",
        title: "Samples",
        hasData: data.length != 0,
      },
      [
        h(PageViewSamples, {
          data,
          isEditing: false,
          draggable,
          onClick: onClickDelete,
          setID,
        }),
      ]
    );
  }
  return h(
    PageViewBlock,
    {
      isEditing,
      modelLink: true,
      onClick: onClickList,
      model: "sample",
      title: "Samples",
      hasData: data.length != 0,
    },
    [
      h(PageViewSamples, {
        data,
        isEditing,
        draggable,
        onClick: onClickDelete,
        setID,
      }),
    ]
  );
};

const SampleContainer = styled.div`\
display: flex;
flex-flow: row wrap;
margin: 0 -5px;\
`;

export const PageViewSamples = function ({
  data,
  isEditing,
  setID = () => {},
  link = true,
  onClick,
  draggable = true,
}) {
  if (data != null) {
    return h("div.sample-area", [
      h(SampleContainer, [
        data.map((d) => {
          const { material, id, name, location_name, session, location } = d;
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
              onClick: () => onClick({ id, name }),
              isEditing,
            }),
          ]);
        }),
      ]),
    ]);
  }
};

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
        ele.technique,
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
export const SampleCard = function (props: SampleCardProps) {
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
    PageViewModelCard,
    {
      link,
      draggable: false,
      className: "sample-card",
      to,
      isEditing,
      onMouseEnter: onHover,
      onMouseLeave: onHoverLeave,
      onClick,
    },
    [
      h("h4.name", name),
      h(Location, { location }),
      h.if(material != null)("div.material", material),
      h(SessionContent, { session }),
    ]
  );
};

export function SubSamplePageView(props) {
  const { sample_id, isEditing } = props;

  let data = useAPIv2Result(
    `/sub-sample/${sample_id}`,
    {},
    { unwrapResponse: data => data.sample_collection }
  );

  if (data == undefined) data = [];

  return h(
    PageViewBlock,
    {
      isEditing,
      title: "Sub-Samples",
      model: "sample",
      hasData: data.length > 0
    },
    [
      h(PageViewSamples, {
        data,
        isEditing,
        onClick: () => {},
        draggable: false
      })
    ]
  );
}
