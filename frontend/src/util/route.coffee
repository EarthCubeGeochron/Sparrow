import {Route} from 'react-router-dom'
import h from 'react-hyperscript'
import {ErrorBoundary} from './error-boundary'

ErrorBoundaryRoute = (props)->
  {component, rest...} = props
  h Route, {
    rest...
    component: (p)->
      h ErrorBoundary, null, (
        h component, p
      )
  }

export {ErrorBoundaryRoute}
