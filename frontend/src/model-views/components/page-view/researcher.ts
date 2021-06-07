import { hyperStyled } from "@macrostrat/hyper";
import { ResearcherEditCard, AddCard } from "../index";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const PageViewResearchers = function({ data, isEditing, onClick }) {
  let content;
  if (data != null) {
    content = h("div", [
      h("h4", { style: { display: "flex", alignItems: "baseline" } }, [
        "Researchers"
      ]),
      data.map(d => h("div.researcher", d.name))
    ]);
  }
  if (isEditing) {
    return h("div.researchers", [
      h("h4", { style: { display: "flex", alignItems: "baseline" } }, [
        "Researchers"
      ]),
      h.if(data.length > 0)("div", [
        data.map(res => {
          const { id, name } = res;
          return h(ResearcherEditCard, { id, name, onClick });
        })
      ])
    ]);
  } else {
    return h("div.researchers", content);
  }
};

export const ResearcherAdd = props => {
  const { onClickDelete, onClickList, data, isEditing = true } = props;

  return h("div", [
    h(PageViewResearchers, {
      onClick: onClickDelete,
      data,
      isEditing
    }),
    h.if(isEditing)(AddCard, {
      model: "researcher",
      onClick: onClickList
    })
  ]);
};
