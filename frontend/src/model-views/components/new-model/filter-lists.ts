import { hyperStyled } from "@macrostrat/hyper";
import { AdminFilter } from "~/filter";
import {
  PublicationAddList,
  ResearcherAddList,
  ProjectListComponent,
  SessionListComponent,
  SampleListComponent,
} from "~/model-views";
import {
  EditProjNewPub,
  EditProjNewResearcher,
  EditProjNewSample,
} from "./index";
//@ts-ignore
import styles from "./module.styl";

const h = hyperStyled(styles);

interface FilterListProps {
  onClick?: (e) => void;
  link?: boolean;
}

export function SampleFilterList({ onClick, link = false }: FilterListProps) {
  const possibleFilters = ["public", "geometry", "date_range"]; //needs to work with "doi_like"

  return h(
    AdminFilter,
    {
      initParams: {},
      possibleFilters,
    },
    [
      !link
        ? h("div.add-button-top", [h(EditProjNewSample, { onSubmit: onClick })])
        : h("div"),
      h(SampleListComponent, {
        componentProps: {
          link,
          onClick,
        },
        params: {},
      }),
    ]
  );
}

export function PublicationFilterList({
  onClick,
  link = false,
}: FilterListProps) {
  const possibleFilters = ["date_range", "doi_like"];

  return h(
    AdminFilter,
    {
      possibleFilters,
      initParams: {},
    },
    [
      h.if(!link)("div.add-button-top", [
        h(EditProjNewPub, { onSubmit: onClick }),
      ]),
      h(PublicationAddList, {
        componentProps: {
          link,
          onClick,
        },
        params: {},
      }),
    ]
  );
}

export function ResearcherFilterList({
  onClick,
  link = false,
}: FilterListProps) {
  const possibleFilters = [];

  return h(
    AdminFilter,
    {
      possibleFilters,
      initParams: {},
    },
    [
      h.if(!link)("div.add-button-top", [
        h(EditProjNewResearcher, { onSubmit: onClick }),
      ]),
      h(ResearcherAddList, {
        componentProps: {
          link,
          onClick,
        },
        params: {},
      }),
    ]
  );
}

export function ProjectFilterList({ onClick, link = false }: FilterListProps) {
  const possibleFilters = ["public", "geometry", "doi_like", "date_range"];

  return h(
    AdminFilter,
    {
      possibleFilters,
      initParams: {},
    },
    [
      h(ProjectListComponent, {
        componentProps: {
          link,
          onClick,
        },
        params: {},
      }),
    ]
  );
}

export function SessionFilterList({ onClick, link = false }: FilterListProps) {
  const possibleFilters = ["public", "date_range", "geometry"];

  return h(
    AdminFilter,
    {
      initParams: {},
      possibleFilters,
    },
    [
      h(SessionListComponent, {
        componentProps: {
          link,
          onClick,
        },
        params: {},
      }),
    ]
  );
}

export function ModelFilterLists(
  props: FilterListProps & { listName: string }
) {
  const { listName, onClick } = props;

  return h("div", [
    h.if(listName === "project")(ProjectFilterList, { onClick }),
    h.if(listName === "sample")(SampleFilterList, { onClick }),
    h.if(listName === "session")(SessionFilterList, { onClick }),
    h.if(listName === "publication")(PublicationFilterList, {
      onClick,
    }),
    h.if(listName === "researcher")(ResearcherFilterList, {
      onClick,
    }),
  ]);
}
