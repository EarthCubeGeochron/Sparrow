//import content from "/build/schema.html";
import content2 from "../../static/ColumnSplitting.html";
import content3 from "../../static/RequestsAndUploads.html";
import content4 from "../../static/CombiningAndExportingToExcel.html";
import content5 from "../../static/DataAnalytics.html";
import content6 from "../../static/Exporting.html";
import content7 from "../../static/MappingWithFolium.html";
import React from "react";

// export const SchemaPage = () => {
//   return (
//     <div className="schema" dangerouslySetInnerHTML={{ __html: content }}></div>
//   );
// };

export const ColumnSplitting = () => {
  return (
    <div
      className="schema"
      dangerouslySetInnerHTML={{ __html: content2 }}
    ></div>
  );
};

export const RequestsAndUploads = () => {
  return (
    <div
      className="schema"
      dangerouslySetInnerHTML={{ __html: content3 }}
    ></div>
  );
};

export const Combine = () => {
  return (
    <div
      className="schema"
      dangerouslySetInnerHTML={{ __html: content4 }}
    ></div>
  );
};
export const DataAnalytics = () => {
  return (
    <div
      className="schema"
      dangerouslySetInnerHTML={{ __html: content5 }}
    ></div>
  );
};
export const Exporting = () => {
  return (
    <div
      className="schema"
      dangerouslySetInnerHTML={{ __html: content6 }}
    ></div>
  );
};
export const Mapping = () => {
  return (
    <div
      className="schema"
      dangerouslySetInnerHTML={{ __html: content7 }}
    ></div>
  );
};

export * from "./environment-variable-list";
