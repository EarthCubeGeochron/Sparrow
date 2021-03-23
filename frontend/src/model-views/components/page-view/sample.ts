import { hyperStyled } from "@macrostrat/hyper";
import styled from "@emotion/styled";
import { Button } from "@blueprintjs/core";
import { AddCard } from "./page-view";
import { SampleCard, SampleEditCard } from "../index";
import { DndChild } from "~/components";
import { useModelURL } from "~/util";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const SampleAdd = (props) => {
  const {
    onClickDelete,
    onClickList,
    data,
    draggable = true,
    isEditing = true,
    setID = () => {},
  } = props;

  return h("div", [
    h("div", [
      h(PageViewSamples, {
        data,
        isEditing,
        draggable,
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
            return h(DndChild, {
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
            });
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

export function NewSamplePageButton() {
  const to = useModelURL("/new-sample");
  const handleClick = (e) => {
    e.preventDefault();
    window.location.href = to;
  };

  return h(
    Button,
    { minimal: true, intent: "success", onClick: handleClick, icon: "add" },
    ["Create New Sample"]
  );
}
