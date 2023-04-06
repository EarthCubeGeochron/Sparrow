import React from "react";
import { hyperStyled } from "@macrostrat/hyper";
import {
  ProjectModelCard,
  SampleModelCard,
  SessionListModelCard,
  DataFileModelCard,
  PublicationModelCard,
  ResearcherModelCard,
} from "~/model-views";
import { InfiniteAPIView } from "~/components/infinite-scroll";
import { APIV2Context, APIV3Context } from "~/api-v2";
//@ts-ignore
import styles from "./main.styl";

const h = hyperStyled(styles);

function ProjectListChildren({
  data,
  componentProps,
}: {
  data: any[];
  componentProps: any;
}) {
  if (!data.length) return null;
  return h(React.Fragment, [
    data.map((dat, i) => {
      return h(ProjectModelCard, { key: i, ...dat, ...componentProps });
    }),
  ]);
}

const ProjectListComponent = ({ params, componentProps = {} }) => {
  return h("div", { style: { padding: "1px" } }, [
    h(
      InfiniteAPIView,
      {
        url: "/models/project",
        params: {},
        filterParams: { ...params },
        context: APIV2Context,
      },
      [h(ProjectListChildren, { data: [], componentProps })]
    ),
  ]);
};

function SampleListChildren({ data, componentProps }) {
  if (!data.length) return null;

  return h(React.Fragment, [
    data.map((dat, i) => {
      return h(SampleModelCard, { ...dat, ...componentProps });
    }),
  ]);
}

function SampleListComponent({ params, componentProps = {} }) {
  return h("div", [
    h(
      InfiniteAPIView,
      {
        url: "/models/sample",
        params: { nest: "session" },
        filterParams: { ...params },
        context: APIV2Context,
      },
      [h(SampleListChildren, { data: [], componentProps })]
    ),
  ]);
}

function SessionListChildren({ data, componentProps }) {
  return h(React.Fragment, [
    data.map((dat, i) => {
      return h(SessionListModelCard, { ...dat, ...componentProps });
    }),
  ]);
}

function SessionListComponent({ params, componentProps = {} }) {
  return h("div", { style: { padding: "1px" } }, [
    h(
      InfiniteAPIView,
      {
        url: "/models/session",
        params: { nest: "instrument,sample" },
        filterParams: { ...params },
        context: APIV2Context,
      },
      [h(SessionListChildren, { data: [], componentProps })]
    ),
  ]);
}

function unwrapDataFileCardData(data) {
  const { basename, file_hash, type, file_mtime: date } = data;
  return { basename, file_hash, type, date };
}

function DataFileListChildren({ data }) {
  return h(React.Fragment, [
    data.map((dat, i) => {
      const dataFileData = unwrapDataFileCardData(dat);
      return h(DataFileModelCard, { ...dataFileData });
    }),
  ]);
}

function DataFilesListComponent({ params }) {
  if ("search" in params) {
    params["like"] = params["search"];
    delete params["search"];
  }
  return h("div", { style: { padding: "1px" } }, [
    h(
      InfiniteAPIView,
      {
        url: "/data_file/list",
        params: {},
        filterParams: { ...params },
        context: APIV2Context,
      },
      [h(DataFileListChildren)]
    ),
  ]);
}

function PublicationAddListChildren({ data, componentProps }) {
  return h(React.Fragment, [
    data.map((dat, i) => {
      return h(PublicationModelCard, { ...dat, ...componentProps });
    }),
  ]);
}

function PublicationAddList({ params, componentProps }) {
  return h("div", [
    h(
      InfiniteAPIView,
      {
        url: "/models/publication",
        params: {},
        filterParams: { ...params },
        context: APIV2Context,
      },
      [h(PublicationAddListChildren, { data: [], componentProps })]
    ),
  ]);
}

function ResearcherAddListChildren({ data, componentProps }) {
  return h(React.Fragment, [
    data.map((dat, i) => {
      return h(ResearcherModelCard, { ...dat, ...componentProps });
    }),
  ]);
}

function ResearcherAddList({ params, componentProps }) {
  return h("div", [
    h(
      InfiniteAPIView,
      {
        url: "/models/researcher",
        params: {},
        filterParams: { ...params },
        context: APIV2Context,
      },
      [h(ResearcherAddListChildren, { data: [], componentProps })]
    ),
  ]);
}

export {
  ProjectListComponent,
  SampleListComponent,
  SessionListComponent,
  DataFilesListComponent,
  PublicationAddList,
  ResearcherAddList,
};
