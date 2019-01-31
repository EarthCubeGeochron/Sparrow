import h from 'react-hyperscript'
import {SiteTitle} from '../shared/util'
import {ProjectListComponent} from './project-component'

ProjectPage = ->
  h 'div', [
    h SiteTitle, {subPage: 'Admin'}
    h ProjectListComponent
  ]

export {ProjectPage}
