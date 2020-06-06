/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {StatefulComponent} from '@macrostrat/ui-components';
import {Component, createContext} from 'react';
import {ErrorBoundary} from '../util';
import T from 'prop-types';
import h from 'react-hyperscript';

const FrameContext = createContext({});

class FrameProvider extends StatefulComponent {
  static initClass() {
    this.propTypes = {
      overrides: T.objectOf(T.node)
    };
    this.defaultProps = {overrides: {}};
  }
  constructor(props){
    {
      // Hack: trick Babel/TypeScript into allowing this before super.
      if (false) { super(); }
      let thisFn = (() => { return this; }).toString();
      let thisName = thisFn.match(/return (?:_assertThisInitialized\()*(\w+)\)*;/)[1];
      eval(`${thisName} = this;`);
    }
    this.getElement = this.getElement.bind(this);
    super(props);
    this.state = {registry: {}};
  }
  render() {
    const value = {register: this.register, getElement: this.getElement};
    return h(FrameContext.Provider, {value}, this.props.children);
  }

  getElement(id){
    const {overrides} = this.props;
    return overrides[id] || null;
  }
}
FrameProvider.initClass();

class Frame extends Component {
  static initClass() {
    this.contextType = FrameContext;
    this.propTypes = {
      id: T.string.isRequired,
      iface: T.object,
      children: T.node,
      rest: T.object
    };
  }
  render() {
    const {id, iface, children, ...rest} = this.props;
    const el = this.context.getElement(id);

    // By default we just render the children
    const defaultContent = children;
    let child = defaultContent;
    if (el != null) {
      // We have an override
      child = el;
    }

    if (typeof child === 'function') {
      child = child({...rest, defaultContent});
    }

    return h(ErrorBoundary, null, child);
  }
}
Frame.initClass();

export {FrameProvider, Frame};
