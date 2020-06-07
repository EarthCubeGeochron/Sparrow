/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Route} from 'react-router-dom';
import h from 'react-hyperscript';
import {ErrorBoundary} from './error-boundary';

const ErrorBoundaryRoute = function(props){
  const {component, ...rest} = props;
  return h(Route, {
    ...rest,
    component(p){
      return h(ErrorBoundary, null, (
        h(component, p)
      ));
    }
  });
};

export {ErrorBoundaryRoute};
