import h from "@macrostrat/hyper";
import { ProjectInfoLink } from "~/model-views/project";
import InfiniteScroll from "~/components/infinite-scroll";
//import { ForeverScroll } from "~/components/infinite-scroll;";
//import { InfiniteScrollView } from "@macrostrat/ui-components";
import { useAPIResult } from "@macrostrat/ui-components";
import { useState, useEffect } from "react";
import { Spinner } from "@blueprintjs/core";
import { SampleListCard } from "../model-views/sample/list";
import { SessionInfoLink } from "../model-views/session/info-card";
import { DataFilesCard } from "../model-views/data-files";

// function that performs an api call
async function getNextPageAPI(nextPage, url, params) {
  try {
    const response = await fetch(url + "?" + params + "&page=" + nextPage);
    const data = await response.json();
    return data;
  } catch (error) {
    console.log(error);
  }
}

// unwraps the data to be simpatico with the ProjectLink component, also gets the next page
function unWrapProjectCardData(data, setPage) {
  const dataObj = data.data.map((obj) => {
    const { id, name, description, publication, session } = obj;
    const samples = session.map((ob) => ob.sample);
    return { id, name, description, publication, samples };
  });
  setPage(data.next_page);
  return dataObj;
}

const params = "nest=publication,session,sample&per_page=15";

const ProjectListComponent = () => {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");

  const url = "http://localhost:5002/api/v2/models/project";

  const initData = useAPIResult(url, {
    nest: "publication,session,sample",
    per_page: 15,
  });

  useEffect(() => {
    if (initData) {
      const dataObj = unWrapProjectCardData(initData, setNextPage);
      setData(dataObj);
    }
  }, [initData]);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, url, params);
    newData.then((res) => {
      const dataObj = unWrapProjectCardData(res, setNextPage);
      const newState = [...data, ...dataObj];
      setData(newState);
    });
  };

  /* List of projects for the catalog. Could potentially move there... */
  return data.length > 0
    ? h(InfiniteScroll, {
        initialData: data,
        component: ProjectInfoLink,
        fetch: fetchNewData,
      })
    : h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
};

function unWrapSampleCardData(data, setPage) {
  const dataObj = data.data.map((obj) => {
    const { id, name, material } = obj;
    return { id, name, material };
  });
  setPage(data.next_page);
  return dataObj;
}

const sampleURL = "http://localhost:5002/api/v2/models/sample";

const sampleParams = "&per_page=15";

//   const { material, id, name } = props;
function SampleListComponent() {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");

  console.log(data);
  console.log(nextPage);

  const initData = useAPIResult<[]>(sampleURL, { per_page: 15 });

  useEffect(() => {
    if (initData) {
      const unwrappedData = unWrapSampleCardData(initData, setNextPage);
      setData(unwrappedData);
    }
  }, [initData]);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, sampleURL, sampleParams);
    newData.then((res) => {
      const dataObj = unWrapSampleCardData(res, setNextPage);
      const newState = [...data, ...dataObj];
      setData(newState);
    });
  };

  return data.length > 0
    ? h(InfiniteScroll, {
        initialData: data,
        component: SampleListCard,
        fetch: fetchNewData,
      })
    : h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
}

// const { id, sample_id, sample_name, target, instrument_name, technique, project_name } = props;
function unWrapSessionCardData(data, setPage) {
  const dataObj = data.data.map((obj) => {
    if (obj.project == null) {
      const {
        id,
        sample: { name: sample_name, id: sample_id },
        technique,
        instrument: { name: instrument_name },
        target,
        date,
      } = obj;
      return {
        id,
        sample_name,
        sample_id,
        technique,
        instrument_name,
        target,
        date,
      };
    } else if (obj.project !== null) {
      const {
        id,
        sample: { name: sample_name, id: sample_id },
        technique,
        instrument: { name: instrument_name },
        target,
        date,
        project: { name: project_name, id: project_id },
      } = obj;
      return {
        id,
        sample_name,
        sample_id,
        technique,
        instrument_name,
        target,
        date,
        project_name,
        project_id,
      };
    }
  });
  setPage(data.next_page);
  return dataObj;
}

const sessionURL = "http://localhost:5002/api/v2/models/session";
const sessionParams = "nest=instrument,project,sample";

// http://localhost:5002/api/v2/models/session?nest=instrument,sample&per_page=15
function SessionListComponent() {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");

  console.log(data);
  console.log(nextPage);

  const initData = useAPIResult<[]>(sessionURL, {
    nest: "instrument,project,sample",
    per_page: 15,
  });

  useEffect(() => {
    if (initData) {
      const unwrappedData = unWrapSessionCardData(initData, setNextPage);
      setData(unwrappedData);
    }
  }, [initData]);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, sessionURL, sessionParams);
    newData.then((res) => {
      const dataObj = unWrapSessionCardData(res, setNextPage);
      const newState = [...data, ...dataObj];
      setData(newState);
    });
  };

  return data.length > 0
    ? h(InfiniteScroll, {
        initialData: data,
        component: SessionInfoLink,
        fetch: fetchNewData,
      })
    : h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
}

const dataFileURL = "http://localhost:5002/api/v2/models/data_file";

const dataFileParams = "nest=data_file_link,sample,session,project&per_page=15";

function unWrapDataFileCardData(data, setPage) {
  const dataObj = data.data.map((obj) => {
    const { basename, file_hash, type } = obj;
    return { basename, file_hash, type };
  });
  setPage(data.next_page);
  return dataObj;
}

// props needed: { basename, file_hash, type }
// http://localhost:5002/api/v2/models/data_file?nest=data_file_link,sample,session,project&per_page=100
function DataFilesListComponent() {
  const [data, setData] = useState([]);
  const [nextPage, setNextPage] = useState("");

  console.log(data);
  console.log(nextPage);

  const initData = useAPIResult<[]>(dataFileURL, {
    nest: "data_file_link,sampel,session,project",
    per_page: 15,
  });

  useEffect(() => {
    if (initData) {
      const unwrappedData = unWrapDataFileCardData(initData, setNextPage);
      setData(unwrappedData);
    }
  }, [initData]);

  const fetchNewData = () => {
    if (!nextPage) return;
    const newData = getNextPageAPI(nextPage, dataFileURL, dataFileParams);
    newData.then((res) => {
      const dataObj = unWrapDataFileCardData(res, setNextPage);
      const newState = [...data, ...dataObj];
      setData(newState);
    });
  };

  return data.length > 0
    ? h(InfiniteScroll, {
        initialData: data,
        component: DataFilesCard,
        fetch: fetchNewData,
      })
    : h("div", { style: { marginTop: "100px" } }, [h(Spinner)]);
}

export {
  ProjectListComponent,
  SampleListComponent,
  SessionListComponent,
  DataFilesListComponent,
};
