import {Tab, Tabs} from '@blueprintjs/core'
import {hyperStyled} from '@macrostrat/hyper'
import styles from './module.styl'

h = hyperStyled(styles)

NewTabs = (props)->
  h Tabs, {
    className: 'tab-panel'
    large: true
    props...
  }

export {NewTabs as Tabs, Tab}
