/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Tab, Tabs} from '@blueprintjs/core';
import {hyperStyled} from '@macrostrat/hyper';
import styles from './module.styl';

const h = hyperStyled(styles);

const NewTabs = props => h(Tabs, {
  className: 'tab-panel',
  large: true,
  ...props
});

export {NewTabs as Tabs, Tab};
