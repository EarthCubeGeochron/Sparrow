import { useContext } from "react";
import h from "@macrostrat/hyper";
import { DataSheetContext } from "./provider";

function Row({ row, children, className }) {
  const { rowHeight } = useContext(DataSheetContext);
  const style = { height: rowHeight };
  return h("tr", { style, className }, [
    h("td.index-cell.cell.read-only.index", row + 1),
    children,
  ]);
}

type ColumnInfo = {
  name: string;
  width: number | null;
};

function HeaderCell({ col }: { col: ColumnInfo }) {
  const { name, width } = col;
  return h("td.cell.header.read-only", name);
}

function Columns({ width }) {
  const { columns } = useContext(DataSheetContext);
  return h("colgroup", [
    h("col.index-column", { key: "index", style: { width: 50 } }),
    columns.map((col) =>
      h("col", { key: col.name, style: { width: col.width } })
    ),
  ]);
}

function Header({ width }) {
  const style = { width };
  const { columns } = useContext(DataSheetContext);

  return h("thead", { style }, [
    h("tr.header", { style }, [
      h("td.index-column.cell.header", ""),
      columns.map((col) => h(HeaderCell, { key: col.name, col })),
    ]),
  ]);
}

function Sheet({ className, children, width }) {
  return h("table", { className, style: { width } }, [
    h(Columns),
    h(Header, { width }),
    h("tbody", children),
  ]);
}

export { Sheet, Row };
