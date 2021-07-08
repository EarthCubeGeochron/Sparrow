import { hyperStyled } from "@macrostrat/hyper";
import { AddCard, PageViewModelCard, PageViewBlock } from "./page-view";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export function Publication(props) {
  const { doi, title } = props;

  const interior = () => {
    let doiAddendum = [];
    if (doi != null) {
      doiAddendum = [
        " – ",
        h("span.doi-info", [
          h("span.label", "DOI:"),
          h("span.doi.bp3-monospace-text", doi)
        ])
      ];
    }
    return h("div.publication", [h("span.title", title), ...doiAddendum]);
  };

  if (doi == null) {
    return h("div.publication", h(interior));
  } else {
    const href = `https://dx.doi.org/${doi}`;
    return h("a.publication", { href, target: "_blank" }, h(interior));
  }
}

const PubCard = props => {
  let { id, title, onClick, isEditing, doi } = props;

  return h(
    PageViewModelCard,
    {
      onClick: () => onClick({ id, title }),
      isEditing,
      link: false,
      styles: { maxWidth: "700px" }
    },
    [h(Publication, { doi, title })]
  );
};

export const PageViewPublications = ({ data, isEditing = false, onClick }) => {
  if (data == null) {
    data = [];
  }
  return h("div.publications", [
    h.if(data.length > 0)("div", [
      data.map((pub, i) => {
        const { id, title, doi } = pub;
        return h(PubCard, {
          key: i,
          id,
          doi,
          title,
          isEditing,
          onClick
        });
      })
    ])
  ]);
};

export const PubAdd = props => {
  const { onClickDelete, onClickList, data, isEditing = true } = props;
  if (!isEditing && data == null) {
    return null;
  }

  let dat;
  if (data == null) {
    dat = [];
  } else {
    dat = data;
  }
  return h(
    PageViewBlock,
    {
      model: "publication",
      onClick: onClickList,
      modelLink: true,
      isEditing,
      title: "Publications",
      hasData: dat.length != 0
    },
    [
      h(PageViewPublications, {
        data,
        isEditing,
        onClick: onClickDelete
      })
    ]
  );
};
