/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from 'react-hyperscript';
import {Component} from 'react';
import {
  Callout, Icon, Card, InputGroup,
  Menu, MenuItem, Popover,
  Button, Position} from '@blueprintjs/core';
import {PagedAPIView, StatefulComponent} from '@macrostrat/ui-components';
import T from 'prop-types';

class FilterListComponent extends StatefulComponent {
  static initClass() {
    this.propTypes = {
      route: T.string.isRequired,
      filterFields: T.objectOf(T.string).isRequired,
      itemComponent: T.elementType.isRequired
    };
  }
  constructor(props){
    super(props);
    this.updateFilter = this.updateFilter.bind(this);
    this.state = {
      filter: '',
      field: Object.keys(this.props.filterFields)[0],
      isSelecting: false
    };
  }

  updateFilter(event){
    const {value} = event.target;
    return this.updateState({filter: {$set: value}});
  }

  render() {
    const {route, filterFields, itemComponent, ...rest} = this.props;
    const {filter, field} = this.state;
    let params = {};
    if ((filter != null) && (filter !== "")) {
      const val = `%${filter}%`;
      params = {[field]: val};
    }

    const menuItems = [];
    const onClick = k=> () => this.updateState({
      field: {$set: k},
      filter: {$set: ''}
    });

    for (let k in filterFields) {
      const v = filterFields[k];
      menuItems.push(h(Button, {minimal: true, onClick: onClick(k)}, v));
    }

    const content = h(Menu, menuItems);
    const position = Position.BOTTOM_RIGHT;

    const rightElement = h(Popover, {content, position}, [
      h(Button, {minimal: true, rightIcon: "caret-down"}, filterFields[field])
    ]);

    const filterBox = h(InputGroup, {
      leftIcon: 'search',
      placeholder: "Filter values",
      value: this.state.filter,
      onChange: this.updateFilter,
      rightElement
    });

    return h(PagedAPIView, {
      className: 'data-frame',
      extraPagination: filterBox,
      params,
      route,
      topPagination: true,
      bottomPagination: true,
      perPage: 10,
      ...rest
    }, data => h('div', null, data.map(d => h(itemComponent, d))));
  }
}
FilterListComponent.initClass();

export {FilterListComponent};