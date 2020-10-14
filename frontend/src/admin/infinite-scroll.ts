import h from "@macrostrat/hyper";
import {
  ProjectInfoLink, //@ts-ignore
} from "~/model-views/project";
import { SampleListCard } from "../model-views/sample/list";
import { DataFilesCard } from "../model-views/data-files";
import { SessionLinkCard } from "../model-views/data-files/page";
import { FilterBox } from "../components/filter-list";
import { InfiniteAPIView } from "../components/infinite-scroll/infinite-api-view";
import { APIV2Context } from "~/api-v2";

// unwraps the data to be simpatico with the ProjectLink component, also gets the next page
function unWrapProjectCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  return dataObj;
}

const ProjectListComponent = () => {
  const filterFields = ["Name", "Samples"];

  /* List of projects for the catalog. Could potentially move there... */
  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: "/models/project",
      unWrapData: unWrapProjectCardData,
      params: { nest: "publication,session,samnple" },
      component: ProjectInfoLink,
      context: APIV2Context,
    }),
  ]);
};

function unWrapSampleCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, material } = obj;
    return { id, name, material };
  });
  return dataObj;
}

function SampleListComponent() {
  const filterFields = ["Name", "Material", "id"];

  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: "/models/sample",
      unWrapData: unWrapSampleCardData,
      params: {},
      component: SampleListCard,
      context: APIV2Context,
    }),
  ]);
}

// const { id, date, target, technique } = props;
function unWrapSessionCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id: session_id, technique, target, date: session_date } = obj;
    return {
      session_id,
      technique,
      target,
      session_date,
    };
  });
  return dataObj;
}

function SessionListComponent() {
  const filterFields = ["Technique", "Date Precision", "Target", "Instrument"];

  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: "/models/session",
      unWrapData: unWrapSessionCardData,
      params: { nest: "instrument,project,sample" },
      component: SessionLinkCard,
      context: APIV2Context,
    }),
  ]);
}

function unWrapDataFileCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { basename, file_hash, type } = obj;
    return { basename, file_hash, type };
  });
  return dataObj;
}

function DataFilesListComponent() {
  const filterFields = ["Type", "Basename", "Upload Date"];

  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: "/models/data_file",
      unWrapData: unWrapDataFileCardData,
      params: { nest: "data_file_link,sample,session,project" },
      component: DataFilesCard,
      context: APIV2Context,
    }),
  ]);
}

export {
  ProjectListComponent,
  SampleListComponent,
  SessionListComponent,
  DataFilesListComponent,
};
