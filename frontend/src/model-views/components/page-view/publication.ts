import { hyperStyled } from "@macrostrat/hyper";
import { AddCard } from "./page-view";
import { PubEditCard } from "../index";
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
          h("span.doi.bp3-monospace-text", doi),
        ]),
      ];
    }
    return h("div.publication", [h("span.title", title), ...doiAddendum]);
  };

  if (doi == null) {
    return h("div.publication", interior);
  } else {
    const href = `https://dx.doi.org/${doi}`;
    return h("a.publication", { href, target: "_blank" }, h(interior));
  }
}

export const PageViewPublications = ({ data, isEditing = false, onClick }) => {
  if (data == null) {
    data = [];
  }
  if (isEditing) {
    return h("div.publications", [
      h("div", { style: { display: "flex", alignItems: "baseline" } }, [
        h("h4", "Publications"),
      ]),
      h.if(data.length > 0)("div", [
        data.map((pub, i) => {
          const { id, title, doi } = pub;
          return h(PubEditCard, {
            key: i,
            id,
            title,
            content: h(Publication, { doi, title }),
            onClick,
          });
        }),
      ]),
    ]);
  }
  return h("div", [
    h.if(data.length)("div.publications", [
      h("h4", "Publications"),
      (data || []).map((d, i) =>
        h(Publication, { key: i, doi: d.doi, title: d.title })
      ),
    ]),
    h.if(data == null)("div.publications", "No publications"),
  ]);
};

export const PubAdd = (props) => {
  const { onClickDelete, onClickList, data, isEditing = true } = props;
  if (!isEditing && data == null) {
    return null;
  }
  return h("div", [
    h("div", [
      h(PageViewPublications, {
        data,
        isEditing,
        onClick: onClickDelete,
      }),
      h.if(isEditing)(AddCard, {
        model: "publication",
        onClick: onClickList,
      }),
    ]),
  ]);
};
