import { useState } from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  ProjectInfoLink, //@ts-ignore
} from "~/model-views/project";
import { SampleListCard } from "../model-views/sample/list";
import { DataFilesCard } from "../model-views/data-files";
import { SessionLinkCard } from "../model-views/data-files/page";
import { FilterBox } from "../components/filter-list";
import { InfiniteAPIView } from "../components/infinite-scroll/infinite-api-view";
import { APIV2Context } from "~/api-v2";
import styles from "./module.styl";
import { AdminFilter } from "../filter";

const h = hyperStyled(styles);

// unwraps the data to be simpatico with the ProjectLink component, also gets the next page
function unwrapProjectCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  return dataObj;
}

const ProjectListComponent = () => {
  const [params, setParams] = useState({});

  const createParams = (params) => {
    setParams(params);
  };

  /* List of projects for the catalog. Could potentially move there... */
  return h("div", { style: { position: "relative" } }, [
    h("div.listcomponent", [
      h(FilterBox, { content: h(AdminFilter, { createParams }) }),
    ]),
    h("div", { style: { padding: "1px" } }, [
      h(InfiniteAPIView, {
        url: "/models/project",
        unwrapData: unwrapProjectCardData,
        params: { nest: "publication,session,samnple" },
        filterParams: { ...params },
        component: ProjectInfoLink,
        context: APIV2Context,
      }),
    ]),
  ]);
};

function unwrapSampleCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id, name, material } = obj;
    return { id, name, material };
  });
  return dataObj;
}

function SampleListComponent() {
  const filterFields = ["Name", "Material", "id"];

  return h("div", [
    h("div.listcomponent", [h(FilterBox, { filterFields })]),
    h("div", [
      h(InfiniteAPIView, {
        url: "/models/sample",
        unwrapData: unwrapSampleCardData,
        params: {},
        filterParams: {},
        component: SampleListCard,
        context: APIV2Context,
      }),
    ]),
  ]);
}

// const { id, date, target, technique } = props;
function unwrapSessionCardData(data) {
  const dataObj = data.data.map((obj) => {
    const { id: session_id, technique, target, date } = obj;
    return {
      session_id,
      technique,
      target,
      date,
    };
  });
  return dataObj;
}

function SessionListComponent() {
  const filterFields = ["Technique", "Date Precision", "Target", "Instrument"];

  return h("div", [
    h("div.listcomponent", [h(FilterBox, { filterFields })]),
    h("div", { style: { padding: "1px" } }, [
      h(InfiniteAPIView, {
        url: "/models/session",
        unwrapData: unwrapSessionCardData,
        params: { nest: "instrument,project,sample" },
        component: SessionLinkCard,
        context: APIV2Context,
        filterParams: {},
      }),
    ]),
  ]);
}

function unwrapDataFileCardData(data) {
  const dataObj = data.data.map((obj) => {
    if (obj.data_file_link.length > 0) {
      const {
        basename,
        file_hash,
        type,
        data_file_link: [{ date }],
      } = obj;
      return { basename, file_hash, type, date };
    }
    const { basename, file_hash, type } = obj;
    return { basename, file_hash, type };
  });
  return dataObj;
}

function DataFilesListComponent() {
  const filterFields = ["Type", "Basename", "Upload Date"];

  return h("div", [
    h("div.listcomponent", [h(FilterBox, { filterFields })]),
    h("div", { style: { padding: "1px" } }, [
      h(InfiniteAPIView, {
        url: "/models/data_file",
        unwrapData: unwrapDataFileCardData,
        params: {
          nest: "data_file_link,sample,session",
          has: "data_file_link",
        },
        filterParams: {},
        component: DataFilesCard,
        context: APIV2Context,
      }),
    ]),
  ]);
}

export {
  ProjectListComponent,
  SampleListComponent,
  SessionListComponent,
  DataFilesListComponent,
};
