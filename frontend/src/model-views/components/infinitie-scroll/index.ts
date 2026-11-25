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
import {
  normalizeProject,
  normalizeSample,
  normalizeSession,
} from "~/api/models";
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
        url: "/project",
        model: "project",
        params: { order: "id.desc" },
        filterParams: { ...params },
        normalize: normalizeProject,
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
        url: "/sample",
        model: "sample",
        params: { order: "id.desc" },
        filterParams: { ...params },
        normalize: normalizeSample,
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
        url: "/session",
        model: "session",
        params: { order: "date.desc,id" },
        filterParams: { ...params },
        normalize: normalizeSession,
      },
      [h(SessionListChildren, { data: [], componentProps })]
    ),
  ]);
}

function unwrapDataFileCardData(data) {
  const { basename, file_hash, type_id: type, file_mtime: date } = data;
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
  return h("div", { style: { padding: "1px" } }, [
    h(
      InfiniteAPIView,
      {
        url: "/data_file",
        model: "data_file",
        params: { order: "file_mtime.desc.nullslast" },
        filterParams: { ...params },
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
        url: "/publication",
        model: "publication",
        params: { order: "id.desc" },
        filterParams: { ...params },
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
        url: "/researcher",
        model: "researcher",
        params: { order: "name" },
        filterParams: { ...params },
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
