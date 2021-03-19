import { hyperStyled } from "@macrostrat/hyper";
import { AddCard } from "./page-view";
import { SampleCard, SampleEditCard } from "../index";
import { DndChild } from "~/components";
import styled from "@emotion/styled";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const SampleAdd = (props) => {
  const {
    onClickDelete,
    onClickList,
    data,
    isEditing = true,
    setID = () => {},
  } = props;

  return h("div", [
    h("div", [
      h(PageViewSamples, {
        data,
        isEditing,
        onClick: onClickDelete,
        setID,
      }),
      h.if(isEditing)(AddCard, {
        model: "sample",
        onClick: onClickList,
      }),
    ]),
  ]);
};

const SampleContainer = styled.div`\
display: flex;
flex-flow: row wrap;
margin: 0 -5px;\
`;

export const PageViewSamples = function({
  data,
  isEditing,
  setID = () => {},
  link = true,
  onClick,
  draggable = true,
}) {
  let content = [h("p", "No samples")];
  if (data != null) {
    if (!isEditing) {
      return h("div.sample-area", [
        h("h4", "Samples"),
        h(SampleContainer, [
          data.map((d) => {
            const { material, id, name, location_name, session } = d;
            return h(SampleCard, {
              material,
              session,
              id,
              name,
              location_name,
              setID,
              link,
            });
          }),
        ]),
      ]);
    } else {
      return h("div.sample-area", [
        h("div", { style: { display: "flex", alignItems: "baseline" } }, [
          h("h4", "Samples"),
        ]),
        h(SampleContainer, [
          data.map((d) => {
            const { id, name, session } = d;
            return h(
              DndChild,
              {
                id,
                data: d,
                draggable,
                childern: h(SampleEditCard, {
                  id,
                  name,
                  session,
                  setID,
                  onClick,
                }),
              },
              [
                h(SampleEditCard, {
                  id,
                  name,
                  setID,
                  onClick,
                }),
              ]
            );
          }),
        ]),
      ]);
    }
  } else {
    if (isEditing) {
      return h("h4", { style: { display: "flex", alignItems: "baseline" } }, [
        "No Samples",
      ]);
    } else {
      return h("h4", "No Samples");
    }
  }
};
