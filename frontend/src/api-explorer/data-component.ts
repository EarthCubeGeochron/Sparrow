/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component} from 'react';
import h from 'react-hyperscript';
import styled from '@emotion/styled';
import {JSONToggle} from './utils';
import {get} from 'axios';
import {JSONCollapsePanel} from './collapse-panel';
import { PagedAPIView } from "@macrostrat/ui-components";
import { Cell, Column, Table } from "@blueprintjs/table";
import ReactJson from 'react-json-view';

import "@blueprintjs/table/lib/css/table.css";

const Bold = styled.span`font-weight:600;`;

class DataTable__ extends Component {
  render() {
    const {data, className} = this.props;
    if ((data == null)) { return null; }

    const columns = [];
    const cellRenderer = column => (function(rowIndex) {
      const dv = data[rowIndex];
      if (dv == null) { return null; }
      let a = dv[column];
      // Special case for JSON rows
      if (typeof a === "object") {
        a = JSON.stringify(a);
      }
      a = `${a}`;
      if (a === 'false') {
        a = h(Bold, null, 'F');
      }
      if (a === 'true') {
        a = h(Bold, null, 'T');
      }
      if (a === 'null') {
        a = '—';
      }

      return h(Cell, null, a);
    });

    const sizes = [];
    for (let k in data[0]) {
      var sz;
      const v = data[0][k];
      columns.push(h(Column, {key: k, name: k, cellRenderer: cellRenderer(k)}));
      if (typeof v === 'boolean') {
        sz = 50;
      } else {
        sz = 100;
      }
      sizes.push(sz);
    }

    return h(Table, {
      numRows: data.length,
      defaultRowHeight: 30,
      columnWidths: sizes,
      className
    }, columns);
  }
}

const DataTable = styled(DataTable__)`\
margin: 1em 0 2em 0;
font-size: 1.2em;\
`;

class APIDataComponentInner extends JSONCollapsePanel {
  constructor(props){
    {
      // Hack: trick Babel/TypeScript into allowing this before super.
      if (false) { super(); }
      let thisFn = (() => { return this; }).toString();
      let thisName = thisFn.match(/return (?:_assertThisInitialized\()*(\w+)\)*;/)[1];
      eval(`${thisName} = this;`);
    }
    this.renderDataInterior = this.renderDataInterior.bind(this);
    super(props);
    this.state = {showJSON: false};
  }

  renderDataInterior(data){
    const {showJSON} = this.state;
    if (showJSON) {
      return h(ReactJson, {src: data});
    }
    return h(DataTable, {data});
  }

  renderInterior() {
    const {route, params} = this.props;
    if (route == null) { return null; }

    return h(PagedAPIView, {
      topPagination: true,
      bottomPagination: false,
      route,
      params,
      perPage: 20
    }, this.renderDataInterior);
  }
}

const APIDataComponent = props => h(APIDataComponentInner, {
  storageID: 'data',
  className: 'data',
  title: 'Data',
  ...props
});

export {APIDataComponent};
