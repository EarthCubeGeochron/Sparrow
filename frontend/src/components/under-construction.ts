/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {NonIdealState} from '@blueprintjs/core';
import h from 'react-hyperscript';

const UnderConstruction = function(props){
  const {name} = props;
  const rest =" view is not yet implemented. Sorry!";
  let desc = "This"+rest;
  if (name != null) {
    desc = h([
      "The ",
      h('b', name),
      rest
    ]);
  }
  return h(NonIdealState, {
    title: "Under construction",
    description: desc,
    icon: 'build'
  });
};

export {UnderConstruction};
