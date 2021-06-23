import { DndContainer } from "~/components";
import { hyperStyled } from "@macrostrat/hyper";
import { useModelURL } from "~/util/router";
import { PageViewModelCard, PageViewBlock, PageViewDate } from "~/model-views";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const SessionAdd = props => {
  const {
    onClickDelete = () => {},
    onClickList = () => {},
    data,
    isEditing = false,
    sampleHoverID = null,
    onDrop = () => {},
    editable = true
  } = props;

  if (!editable) {
    return h(
      PageViewBlock,
      {
        onClick: onClickList,
        isEditing: false,
        title: "Sessions",
        model: "session",
        hasData: data.length != 0
      },
      [
        h(PageViewSessions, {
          session: data,
          onClick: onClickDelete,
          sampleHoverID,
          onDrop,
          isEditing
        })
      ]
    );
  }

  return h(
    PageViewBlock,
    {
      modelLink: true,
      onClick: onClickList,
      isEditing,
      title: "Sessions",
      model: "session",
      hasData: data.length != 0
    },
    [
      h(PageViewSessions, {
        session: data,
        onClick: onClickDelete,
        sampleHoverID,
        onDrop,
        isEditing
      })
    ]
  );
};

export function PageViewSessions(props) {
  const {
    isEditing,
    session,
    onClick,
    sampleHoverID = null,
    onDrop = () => {}
  } = props;

  if (!session || session.length == 0) return null;
  return h("div.parameter", [
    h("div.session-container", [
      session.map(obj => {
        const {
          id: session_id,
          technique,
          target,
          date,
          analysis,
          data,
          sample
        } = obj;
        const onHover =
          sampleHoverID && sample ? sample.id == sampleHoverID : false;
        return h(
          DndContainer,
          {
            id: session_id,
            onDrop
          },
          [
            h(SessionCard, {
              session_id,
              isEditing,
              sample,
              technique,
              target,
              date,
              onClick,
              onHover
            })
          ]
        );
      })
    ])
  ]);
}

export const SessionCard = props => {
  const {
    onClick,
    session_id,
    target,
    date,
    technique,
    sample = null,
    onHover = false,
    isEditing
  } = props;

  const classname = onHover ? "sample-edit-card-samhover" : "sample-edit-card";

  const sampleName = sample ? sample.name : "";

  const to = useModelURL(`/session/${session_id}`);

  return h("div", [
    h(
      PageViewModelCard,
      {
        to,
        isEditing,
        onClick: () => onClick({ session_id, date }),
        link: true
      },
      [
        h("div", { className: classname }, [
          h("div.session-info", [
            h("div", [h(PageViewDate, { date }), target]),
            h("div", technique)
          ])
        ])
      ]
    ),
    h.if(sample)("div", { style: { fontSize: "10px", marginLeft: "10px" } }, [
      h("i", `Linked through ${sampleName}`)
    ])
  ]);
};
