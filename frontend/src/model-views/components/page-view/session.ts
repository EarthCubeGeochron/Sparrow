import { AddCard, SessionPageViewModelCard, SessionEditCard } from "../index";
import { DndContainer } from "~/components";
import { hyperStyled } from "@macrostrat/hyper";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const SessionAdd = (props) => {
  const {
    onClickDelete,
    onClickList,
    data,
    isEditing,
    sampleHoverID = null,
    onDrop = () => {},
  } = props;

  return h("div", [
    h(PageViewSessions, {
      session: data,
      onClick: onClickDelete,
      sampleHoverID,
      onDrop,
      isEditing,
    }),
    h.if(isEditing)(AddCard, {
      model: "session",
      onClick: onClickList,
    }),
  ]);
};

export function PageViewSessions(props) {
  const {
    isEditing,
    session,
    onClick,
    sampleHoverID = null,
    onDrop = () => {},
  } = props;

  if (session == null && !isEditing) return null;
  if (session == null && isEditing) {
    return h("div.parameter", [h("h4.subtitle", "Sessions")]);
  }
  return h("div.parameter", [
    h.if(session.length > 0 || isEditing)("h4.subtitle", "Sessions"),
    h("div.session-container", [
      session.map((obj) => {
        const {
          id: session_id,
          technique,
          target,
          date,
          analysis,
          data,
          sample,
        } = obj;
        const onHover =
          sampleHoverID && sample ? sample.id == sampleHoverID : false;
        if (isEditing) {
          return h(
            DndContainer,
            {
              id: session_id,
              onDrop,
            },
            [
              h(SessionEditCard, {
                session_id,
                sample,
                technique,
                target,
                date,
                onClick,
                onHover,
              }),
            ]
          );
        } else {
          return h(SessionPageViewModelCard, {
            session_id,
            technique,
            target,
            date,
            data,
            analysis,
            sample,
            onHover,
          });
        }
      }),
    ]),
  ]);
}
