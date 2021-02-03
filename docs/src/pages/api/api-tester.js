import React, { useState, useEffect, useRef } from "react";
import { useAPIResult } from "@macrostrat/ui-components";
import Layout from "@theme/Layout";
import styles from "./api.module.css";

// const routes = [
//   { name: "/sample" },
//   { name: "/session" },
//   { name: "/datum" },
//   { name: "/analysis" },
//   { name: "/attribute" },
//   { name: "/age_datum" },
//   { name: "/material" },
// ];
const baseURL = "https://sparrow-data.org/labs/wiscar/api/v1/";

function APITester() {
  const [state, setState] = useState({
    query: "",
    params: "",
    param: "",
    routes: "",
  });
  const { routes, params, query, param } = state;
  //console.log(state);

  let response = useAPIResult(baseURL + query);
  console.log(response);

  useEffect(() => {
    if (response && !query) {
      const { routes } = response;
      const route = routes.map((obj) => obj.route);
      setState({ ...state, routes: route });
    }
  }, [response, query]);

  useEffect(() => {
    if (query !== "") {
      const args = response.arguments;
      if (args) {
        const params = args.map((arg) => "?" + arg.name);
        //console.log(params);
        setState({ ...state, params });
      }
    }
  }, [query, response]);

  const resetClick = () => {
    setState({ ...state, query: "", params: "", param: "" });
  };

  const QueryButtons = () => {
    return (
      <div className={styles.routes}>
        <h2>Routes:</h2>
        {routes
          ? routes.map((route) => {
              return (
                <button
                  key={route}
                  className={styles.routebtn}
                  onClick={() => setState({ ...state, query: route.slice(1) })}
                >
                  {route}
                </button>
              );
            })
          : null}
        <button onClick={resetClick} className={styles.resetbtn}>
          Reset URL
        </button>
      </div>
    );
  };

  const ParamButtons = () => {
    return (
      <div className={styles.routes}>
        <h2>Params:</h2>
        {params
          ? params.map((param) => {
              return (
                <button
                  key={param}
                  className={styles.routebtn}
                  onClick={() => setState({ ...state, param: param })}
                >
                  {param}
                </button>
              );
            })
          : null}
      </div>
    );
  };

  return (
    <Layout>
      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "20px" }}
      >
        <h1 className={styles.title}>API Payground</h1>
      </div>
      <div className={styles.container}>
        <QueryButtons />
        {params ? <ParamButtons /> : null}
        <div className={styles.output}>
          <h1>OutputArea</h1>
          <h3>{baseURL + query + param}</h3>
          <div>JSON Data</div>
        </div>
      </div>
    </Layout>
  );
}

export default APITester;
