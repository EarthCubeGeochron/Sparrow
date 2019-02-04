import h from 'react-hyperscript'
import {Component} from 'react'
import {ProjectListComponent} from './project-component'

class AdminBase extends Component
  render: ->
    h ProjectListComponent

export {AdminBase}
