import h from "@macrostrat/hyper";
import {
  ProjectInfoLink, //@ts-ignore
} from "~/model-views/project";
//import { ForeverScroll } from "~/components/infinite-scroll;";
//import { InfiniteScrollView } from "@macrostrat/ui-components";
import { useAPIResult } from "@macrostrat/ui-components";
import { useState, useEffect } from "react";
import { Spinner } from "@blueprintjs/core";
import { SampleListCard } from "../model-views/sample/list";
import { SessionInfoLink } from "../model-views/session/info-card";
import { DataFilesCard } from "../model-views/data-files";
import { SessionLinkCard } from "../model-views/data-files/page";
import { FilterBox } from "../components/filter-list";
import { InfiniteAPIView } from "../components/infinite-scroll/infinite-api-view";

// unwraps the data to be simpatico with the ProjectLink component, also gets the next page
function unWrapProjectCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  return dataObj;
}

const projectParams = "nest=publication,session,sample&per_page=15";
const projectURL = "http://localhost:5002/api/v2/models/project";
const projectNest = "publication,session,sample";

const ProjectListComponent = () => {
  const filterFields = ["Name", "Samples"];

  /* List of projects for the catalog. Could potentially move there... */
  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: projectURL,
      nest: projectNest,
      unWrapData: unWrapProjectCardData,
      params: projectParams,
      component: ProjectInfoLink,
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

const sampleURL = "http://localhost:5002/api/v2/models/sample";

//   const { material, id, name } = props;
function SampleListComponent() {
  const filterFields = ["Name", "Material", "id"];

  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: sampleURL,
      nest: "",
      unWrapData: unWrapSampleCardData,
      params: "",
      component: SampleListCard,
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

const sessionURL = "http://localhost:5002/api/v2/models/session";
const sessionParams = "nest=instrument,project,sample";
const sessionNest = "instrument,project,sample";

// http://localhost:5002/api/v2/models/session?nest=instrument,sample&per_page=15
function SessionListComponent() {
  const filterFields = ["Technique", "Date Precision", "Target", "Instrument"];

  return h("div", [
    h("div", { style: { paddingTop: "10px" } }, [
      h(FilterBox, { filterFields }),
    ]),
    h(InfiniteAPIView, {
      url: sessionURL,
      nest: sessionNest,
      unWrapData: unWrapSessionCardData,
      params: sessionParams,
      component: SessionLinkCard,
    }),
  ]);
}

const dataFileURL = "http://localhost:5002/api/v2/models/data_file";
const dataFileParams = "nest=data_file_link,sample,session,project&per_page=15";
const dataFileNest = "data_file_link,sampel,session,project";

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
      url: dataFileURL,
      nest: dataFileNest,
      unWrapData: unWrapDataFileCardData,
      params: dataFileParams,
      component: DataFilesCard,
    }),
  ]);
}

export {
  ProjectListComponent,
  SampleListComponent,
  SessionListComponent,
  DataFilesListComponent,
};
