import { useContext } from "react";
import h from "@macrostrat/hyper";
import { DataSheetContext } from "./provider";

function Row({ row, children, className }) {
  const { rowHeight } = useContext(DataSheetContext);
  const style = { height: rowHeight };
  return h("tr", { style, className }, [
    h("td", { className: "cell read-only" }, row + 1),
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
    "td.cell",
    {
      key: name,
      style: { width },
    },
    name
  );
}

function Header({ width }) {
  const style = { width };
  const { columns } = useContext(DataSheetContext);

  return h("thead", { style }, [
    h("tr", { className: "header", style }, [
      h("td", "Index"),
      columns.map((col) => h(HeaderCell, { col })),
    ]),
  ]);
}

function Sheet({ className, children, width }) {
  return h("table", { className, style: { width } }, [
    h(Header, { width }),
    h("tbody", children),
  ]);
}

export { Sheet, Row };
