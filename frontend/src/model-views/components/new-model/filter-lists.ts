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

  return h(AdminFilter, {
    addModelButton: h.if(!link)("div.add-button-top", [
      h(EditProjNewSample, { onSubmit: onClick }),
    ]),
    componentProps: {
      link,
      onClick,
    },
    listComponent: SampleListComponent,
    possibleFilters,
  });
}

export function PublicationFilterList({
  onClick,
  link = false,
}: FilterListProps) {
  const possibleFilters = ["date_range", "doi_like"];

  return h(AdminFilter, {
    addModelButton: h.if(!link)("div.add-button-top", [
      h(EditProjNewPub, { onSubmit: onClick }),
    ]),
    listComponent: PublicationAddList,
    componentProps: {
      link,
      onClick,
    },
    possibleFilters,
  });
}

export function ResearcherFilterList({
  onClick,
  link = false,
}: FilterListProps) {
  const possibleFilters = [];

  return h(AdminFilter, {
    addModelButton: h.if(!link)("div.add-button-top", [
      h(EditProjNewResearcher, { onSubmit: onClick }),
    ]),
    listComponent: ResearcherAddList,
    componentProps: {
      link,
      onClick,
    },
    possibleFilters,
  });
}

export function ProjectFilterList({ onClick, link = false }: FilterListProps) {
  const possibleFilters = ["public", "geometry", "doi_like", "date_range"];

  return h(AdminFilter, {
    listComponent: ProjectListComponent,
    componentProps: {
      link,
      onClick,
    },
    possibleFilters,
  });
}

export function SessionFilterList({ onClick, link = false }: FilterListProps) {
  const possibleFilters = ["public", "date_range", "geometry"];

  return h(AdminFilter, {
    listComponent: SessionListComponent,
    componentProps: {
      link,
      onClick,
    },
    possibleFilters,
  });
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
