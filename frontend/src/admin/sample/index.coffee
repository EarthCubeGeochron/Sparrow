import {Component} from 'react'
import h from 'react-hyperscript'
import {Route, Switch} from 'react-router-dom'
import {SamplePage} from './page'
import {SampleList} from './list'

class SampleMain extends Component
  render: ->
    {match} = @props
    base = match.path
    # Render main body
    h Switch, [
      h Route, {
        path: base+"/:id"
        component: SamplePage
      }
      h Route, {
        path: base
        component: SampleList
        exact: true
      }
    ]

export {SampleMain, SamplePage, SampleList}
export * from './detail-card'
