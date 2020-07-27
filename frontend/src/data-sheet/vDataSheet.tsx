import React from "react";
import ReactDataSheet, { DataCell } from "react-datasheet";
import "react-datasheet/lib/react-datasheet.css";
import { Component } from "react";

class VirDataSheet extends ReactDataSheet {
  _setState(state) {
    super._setState(state);

    this.grid.forceUpdateGrids();
  }
  render() {
    const {
      sheetRenderer: SheetRenderer,
      rowRenderer: RowRenderer,
      cellRenderer,
      dataRenderer,
      valueRenderer,
      dataEditor,
      valueViewer,
      attributesRenderer,
      className,
      overflow,
      data,
      keyFn,
      ...rest
    } = this.props;
    const { forceEdit } = this.state;

    return (
      <span
        ref={(r) => {
          this.dgDom = r;
        }}
        tabIndex="0"
        className="data-grid-container"
        onKeyDown={this.handleKey}
      >
        <SheetRenderer
          data={data}
          className={["data-grid", className, overflow]
            .filter((a) => a)
            .join(" ")}
          virtualRowRenderer={({ key, index: i, style }) => {
            const row = data[i];
            return (
              <RowRenderer
                style={style}
                key={keyFn ? keyFn(i) : i}
                row={i}
                cells={row}
              >
                {row.map((cell, j) => {
                  return (
                    <DataCell
                      key={cell.key ? cell.key : `${i}-${j}`}
                      row={i}
                      col={j}
                      cell={cell}
                      forceEdit={forceEdit}
                      onMouseDown={this.onMouseDown}
                      onMouseOver={this.onMouseOver}
                      onDoubleClick={this.onDoubleClick}
                      onContextMenu={this.onContextMenu}
                      onChange={this.onChange}
                      onRevert={this.onRevert}
                      onNavigate={this.handleKeyboardCellMovement}
                      onKey={this.handleKey}
                      selected={this.isSelected(i, j)}
                      editing={this.isEditing(i, j)}
                      clearing={this.isClearing(i, j)}
                      attributesRenderer={attributesRenderer}
                      cellRenderer={cellRenderer}
                      valueRenderer={valueRenderer}
                      dataRenderer={dataRenderer}
                      valueViewer={valueViewer}
                      dataEditor={dataEditor}
                    />
                  );
                })}
              </RowRenderer>
            );
          }}
        />
      </span>
    );
  }
}

export default VirDataSheet;
