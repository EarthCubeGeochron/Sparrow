import { useContext } from "react";
import h from "@macrostrat/hyper";
import { DataSheetContext } from "./provider";

function Row({ row, children, className }) {
  const { rowHeight } = useContext(DataSheetContext);
  const style = { height: rowHeight };
  return h("tr", { style, className }, [
    h("td.index-cell", { className: "cell read-only" }, row + 1),
    children,
  ]);
}

type ColumnInfo = {
  name: string;
  width: number | null;
};

function HeaderCell({ col }: { col: ColumnInfo }) {
  const { name, width } = col;
  return h(
    "td.cell.read-only",
    {
      key: name,
      style: { width },
    },
    name
  );
}

function Columns({ width }) {
  const { columns } = useContext(DataSheetContext);
  return h("colgroup", [
    h("col.index-column", { style: { width: 50 } }),
    columns.map((col) => h("col", { style: { width: 100 } })),
  ]);
}

function Header({ width }) {
  const style = { width };
  const { columns } = useContext(DataSheetContext);

  return h("thead", { style }, [
    h("tr", { className: "header", style }, [
      h("td.index-column.cell.read-only", ""),
      columns.map((col) => h(HeaderCell, { col })),
    ]),
  ]);
}

function Sheet({ className, children, width }) {
  return h("table", { className, style: { width: 500 } }, [
    h(Columns),
    h(Header, { width }),
    h("tbody", children),
  ]);
}

export { Sheet, Row };
