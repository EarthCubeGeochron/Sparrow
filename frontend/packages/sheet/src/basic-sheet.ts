import h from "@macrostrat/hyper";
import ReactDataSheet from "react-datasheet";
import "react-datasheet/lib/react-datasheet.css";
import { createContext, useContext } from "react";

export interface Field<Key> {
  name: string;
  key: Key;
  required?: boolean;
  isValid?(k: any): boolean;
  transform?(k: any): any;
  dataEditor?: ReactDataSheet.DataEditor<ReactDataSheet.Cell<any, any>>;
}

const FieldContext = createContext<Field<string>[]>([]);
function FieldProvider({ fields, children }) {
  return h(FieldContext.Provider, { value: fields }, children);
}

const useFields = () => useContext(FieldContext);

function Columns({ fields }) {
  return h("colgroup", [
    h("col.index-column", { key: "index" }),
    fields.map(({ key }) => {
      return h("col", {
        className: key,
        key,
      });
    }),
  ]);
}

function Row(props) {
  const { children, row } = props;
  return h("tr", [h("td.index-cell.cell.read-only.index", row + 1), children]);
}

function Header({ fields }) {
  return h("thead", [
    h("tr.header", [
      h("td.index-column.cell.read-only", ""),
      fields.map((col, index) => {
        return h(
          "td.cell.header.read-only.header-cell",
          {
            key: col.key,
            index,
          },
          col.name
        );
      }),
    ]),
  ]);
}

function Sheet({ className, children }) {
  const fields = useFields();
  return h("table", { className }, [
    h(Columns, { fields }),
    h(Header, { fields }),
    h("tbody", children),
  ]);
}

export function getFieldData<K>(field: Field<K>): Field<K> {
  const {
    transform = (d) => parseFloat(d),
    isValid = (d) => !isNaN(d),
    required = true,
    ...rest
  } = field;
  return { ...rest, transform, isValid, required };
}

function getDefaultFields(data: object[]) {
  let fields = [];
  for (const key of Object.keys(data[0])) {
    fields.push({
      name: key,
      key: key,
      transform(d) {
        const num = parseFloat(d);
        if (!isNaN(num)) {
          return num.toPrecision(5);
        }
        return d;
      },
    });
  }
  return fields;
}

function expandData(data, fields) {
  return data.map((d, i) => {
    return fields.map((field) => {
      let value = d[field.key];
      return { value: field.transform?.(value) ?? value };
    });
  });
}

export default function BasicDataSheet({
  data,
  fields,
  className,
}): React.ReactNode {
  const nextFields = fields ?? getDefaultFields(data);
  const expandedData = expandData(data, nextFields);
  if (nextFields == null || expandedData == null) return null;
  console.log(nextFields, expandedData);
  return h(
    FieldProvider,
    { fields: nextFields },
    h(ReactDataSheet, {
      className,
      data: expandedData,
      valueRenderer: (cell, row, col) => {
        return cell.value;
      },
      rowRenderer: Row,
      sheetRenderer: Sheet,
      attributesRenderer(cell, row, col) {
        if (cell.value == null || cell.value == "")
          return { "data-status": "empty" };
        const { isValid } = getFieldData(nextFields[col]);
        const status = isValid(cell.value) ? "ok" : "invalid";
        return { "data-status": status };
      },
    })
  );
}
