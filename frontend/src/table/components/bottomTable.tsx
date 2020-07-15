import React, {useState, useRef} from "react";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import TableFooter from "@material-ui/core/TableFooter";
import { Tab, Button } from "@material-ui/core";
import TablePagination from "@material-ui/core/TablePagination";
import { usePagination, useTable, useRowSelect } from "react-table";
import Checkbox from "@material-ui/core/Checkbox";
import TablePaginationActions from "./tablePagnation";


function TableBottom({ data, columns, updateMyData, id }) {
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
    useRowSelect,
    state: { pageIndex, pageSize, rowState, rowIndex },
  } = useTable(
    {
      columns,
      data,
      updateMyData,
      id,
    },
    (hooks) => {
      hooks.allColumns.push((columns) => [
        {
          id: "selection",
          Cell: ({ row }) => (
            <div>
              {/* <Button
                onClick={() =>
                  updateMyData(
                    EditableCell.row,
                    EditableCell.column,
                    EditableCell.value
                  )
                }
                {...row.getRowProps()}
              >
                Save
              </Button> */}
            </div>
          ),
        },
        ...columns,
      ]);
    }
  );

  const buttonRef = useRef();

  const TableBottom = () => {
    return (
      <div>
        <Button
          onClick={() => {
            console.log(buttonRef.current);
          }}
        >
          Save Changes
        </Button>
        <Table>
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
            {data.map((row, i) => {
              prepareRow(row);
              return (
                <TableRow {...row.getRowProps()}>
                  <Button>Save</Button> 
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
        </Table>
      </div>
    );
  };

  return (
    <div>
      <TableBottom></TableBottom>
    </div>
  );
}

export default TableBottom;
