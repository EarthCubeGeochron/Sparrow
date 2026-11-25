import { Button } from "@blueprintjs/core";
import { hyperStyled } from "@macrostrat/hyper";
import { useModelURL } from "~/util";
import { usePublication } from "~/api/models";
import { pluralize } from "../new-model";
import { ModelLinkCard, PageViewBlock } from "~/model-views";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

export const ProjectAdd = (props) => {
  const { onClickDelete, onClickList, data, isEditing } = props;

  return h(
    PageViewBlock,
    {
      model: "project",
      onClick: onClickList,
      isEditing,
      title: "Project",
      modelLink: true,
      hasData: data.project.length != 0,
    },
    [
      h(PageViewProjects, {
        onClick: onClickDelete,
        isEditing,
        data,
      }),
    ]
  );
};

export const PageViewProjects = ({ data, isEditing, onClick }) => {
  return h("div", [h(ProjectCard, { d: data, onClick, isEditing })]);
};

const ProjectCard = (props) => {
  const { d, onClick, isEditing } = props;

  const project = d.project.map((obj) => {
    if (obj) {
      const { name, id, session, publication, description, sample } = obj;
      return { name, id, session, publication, description, sample };
    }
    return null;
  });

  return h("div", [
    project.map((obj) => {
      if (!obj) return null;
      const { name, id } = obj;
      const to = useModelURL(`/project/${id}`);

      return h(
        ModelLinkCard,
        {
          key: id,
          isEditing,
          styles: { minWidth: "500px" },
          to,
          link: true,
          onClick: () => onClick({ id, name }),
        },
        [h(ProjectCardContent, { ...obj, long: false })]
      );
    }),
  ]);
};

export function pubTitles({ publication }) {
  // Publications arrive either as records or as bare ids
  const pub = publication[0];
  const fetched = usePublication(typeof pub == "object" ? null : pub);
  const title = typeof pub == "object" ? pub?.title : fetched?.title;
  if (title == null) return null;
  if (publication.length > 1) return title + "....";
  return title;
}

export function ProjectCardContent(props) {
  const {
    id,
    name,
    description,
    sample = [],
    session = [],
    publication = [],
    long = true,
  } = props;

  const pubData = pubTitles({ publication });

  if (long) {
    return h("div.project-card", [
      h("h4", name),
      h("p.description", description),
      h.if(sample.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [sample.length + " " + pluralize("Sample", sample)]),
        ]),
      ]),
      h.if(publication.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [
            publication.length + " " + pluralize("Publication", publication),
          ]),
          pubData,
        ]),
      ]),
      h.if(session.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [
            session.length + " " + pluralize("Session", session),
          ]),
        ]),
      ]),
    ]);
  } else {
    return h("div.project-card", { style: { margin: 0 } }, [
      h("h4", name),
      h("p.description", description),
      h.if(sample.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [sample.length + " " + pluralize("Sample", sample)]),
        ]),
      ]),
      h.if(publication.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [
            publication.length + " " + pluralize("Publication", publication),
          ]),
        ]),
      ]),
      h.if(session.length > 0)("div.content-area", [
        h("h5", [
          h("span.count", [
            session.length + " " + pluralize("Session", session),
          ]),
        ]),
      ]),
    ]);
  }
}
