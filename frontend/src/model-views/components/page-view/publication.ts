import { hyperStyled } from "@macrostrat/hyper";
import { PubEditCard } from "../index";
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
    return h(interior);
  } else {
    const href = `https://dx.doi.org/${doi}`;
    return h("a.publication", { href, target: "_blank" }, h(interior));
  }
}

export const ModelPublications = function({
  data,
  isEditing = false,
  onClick,
  rightElement,
}) {
  if (data == null) {
    data = [];
  }
  if (isEditing) {
    return h("div.publications", [
      h("div", { style: { display: "flex", alignItems: "baseline" } }, [
        h("h4", "Publications"),
        rightElement,
      ]),
      data.length > 0
        ? data.map((pub) => {
            const { id, title, doi } = pub;
            return h(PubEditCard, {
              id,
              title,
              content: h(Publication, { doi, title }),
              onClick,
            });
          })
        : null,
    ]);
  }
  return h([
    h.if(data.length)("div.publications", [
      h("h4", "Publications"),
      (data || []).map((d, i) =>
        h(Publication, { key: i, doi: d.doi, title: d.title })
      ),
    ]),
    h.if(data == null)("div.publications", "No publications"),
  ]);
};
