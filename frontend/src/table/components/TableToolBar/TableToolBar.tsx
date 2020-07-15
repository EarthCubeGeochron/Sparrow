import React from "react";
import ToolBar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";
import Tooltip from "@material-ui/core/Tooltip";
import AddSample from "./AddSample";
import GlobalFilter from "./GlobalFilter";

const TableToolBar = (props) => {
  const {
    addSampleHandler,
    preGlobalFilteredRows,
    setGlobalFilter,
    globalFilter,
  } = props;
  return (
    <ToolBar>
      <AddSample addSampleHandler={addSampleHandler} />
      <Typography varient="h6" d="TableTitle">
        Add A New Sample
      </Typography>
      <GlobalFilter
        preGlobalFilteredRows={preGlobalFilteredRows}
        globalFilter={globalFilter}
        setGlobalFilter={setGlobalFilter}
      />
    </ToolBar>
  );
};

export default TableToolBar;
