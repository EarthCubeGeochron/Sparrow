import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import TableFooter from "@material-ui/core/TableFooter";
import { Tab } from "@material-ui/core";
import TablePagination from "@material-ui/core/TablePagination";
import {
  usePagination,
  useTable,
  useRowSelect,
  useRowState,
  useGlobalFilter,
} from "react-table";
import Checkbox from "@material-ui/core/Checkbox";
import Buttom from "@material-ui/core/Button";
import TablePaginationActions from "./TablePaginationActions";
import TableBottom from "./TableBottom";
import TableToolBar from "../TableToolBar/TableToolBar";

function TableUI({
  data,
  setData,
  columns,
  columns2,
  skipPageResetRef,
  updateMyData,
}) {
  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    page,
    gotoPage,
    setPageSize,
    setRowState,
    selectedFlatRows,
    preGlobalFilteredRows,
    setGlobalFilter,
    state: { pageIndex, pageSize, selectedRowIds, rowState, globalFilter },
  } = useTable(
    {
      columns2,
      columns,
      data,
      updateMyData,
      autoResetPage: !skipPageResetRef.current,
      autoResetRowState: true,
      autoResetSelectedRows: false,
    },
    useGlobalFilter,
    useRowState,
    usePagination,
    useRowSelect,
    (hooks) => {
      hooks.allColumns.push((columns) => [
        {
          id: "selection",
          Header: ({ getToggleAllRowsSelectedProps }) => (
            <div>
              <Checkbox {...getToggleAllRowsSelectedProps()} />
            </div>
          ),
          Cell: ({ row }) => (
            <div>
              <Checkbox {...row.getToggleRowSelectedProps()} />
            </div>
          ),
        },
        ...columns,
      ]);
    }
  );

  const handleChangePage = (event, newPage) => {
    gotoPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setPageSize(Number(event.target.value));
  };

  const addSampleHandler = (newSample) => {
    const newData = data.concat([newSample]);
    setData(newData);
  };

  const TableTop = () => {
    return (
      <div>
        <Table {...getTableProps()}>
          <TableHead>
            {headerGroups.map((headerGroup) => (
              <TableRow {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <TableCell {...column.getHeaderProps()}>
                    {column.render("Header")}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {page.map((row, i) => {
              prepareRow(row);
              return (
                <TableRow {...row.getRowProps()}>
                  {row.cells.map((cell) => {
                    return (
                      <TableCell {...cell.getCellProps()}>
                        {cell.render("Cell")}
                      </TableCell>
                    );
                  })}
                </TableRow>
              );
            })}
          </TableBody>
          <TableFooter>
            <TableRow>
              <TablePagination
                rowsPerPageOptions={[
                  5,
                  10,
                  25,
                  { label: "All", value: data.length },
                ]}
                colSpan={3}
                count={data.length}
                rowsPerPage={pageSize}
                page={pageIndex}
                SelectProps={{
                  inputProps: { "aria-label": "rows per page" },
                  native: true,
                }}
                onChangePage={handleChangePage}
                onChangeRowsPerPage={handleChangeRowsPerPage}
                ActionsComponent={TablePaginationActions}
              />
            </TableRow>
          </TableFooter>
        </Table>
      </div>
    );
  };

  return (
    <div>
      <TableToolBar
        addSampleHandler={addSampleHandler}
        preGlobalFilteredRows={preGlobalFilteredRows}
        setGlobalFilter={setGlobalFilter}
        globalFilter={globalFilter}
      />
      <TableTop></TableTop>
      <br></br>
      <TableBottom
        data={selectedFlatRows}
        id={selectedRowIds}
        columns={columns2}
        updateMyData={updateMyData}
      ></TableBottom>
    </div>
  );
}

export default TableUI;
