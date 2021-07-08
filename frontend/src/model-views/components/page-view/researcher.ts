import { hyperStyled } from "@macrostrat/hyper";
import { PageViewModelCard, AddCard, PageViewBlock } from "../index";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

const ResearcherCard = (props) => {
  let { id, name, onClick, isEditing } = props;

  return h(
    PageViewModelCard,
    { isEditing, link: false, onClick: () => onClick({ id, name }) },
    [h("h4.name", name)]
  );
};

export const PageViewResearchers = function ({ data, isEditing, onClick }) {
  if (!data) return null;

  return h("div.researchers", [
    h.if(data.length > 0)("div", [
      data.map((res) => {
        const { id, name } = res;
        return h(ResearcherCard, { key: id, id, isEditing, name, onClick });
      }),
    ]),
  ]);
};

export const ResearcherAdd = (props) => {
  const { onClickDelete, onClickList, data, isEditing = true } = props;

  return h(
    PageViewBlock,
    {
      model: "researcher",
      onClick: onClickList,
      isEditing,
      modelLink: true,
      title: "Researchers",
      hasData: data.length != 0,
    },
    [
      h(PageViewResearchers, {
        onClick: onClickDelete,
        data,
        isEditing,
      }),
    ]
  );
};
