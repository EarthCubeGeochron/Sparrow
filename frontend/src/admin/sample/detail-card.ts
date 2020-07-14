/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import {Component, createElement} from 'react';
import {hyperStyled} from '@macrostrat/hyper';
import {Card, Colors} from '@blueprintjs/core';
import {LinkCard} from '@macrostrat/ui-components';
import styles from './module.styl';

const h = hyperStyled(styles);

const SampleCard = function(props){
  let {material, id, name, location_name, link} = props;
  console.log(props);
  if (link == null) { link = true; }
  const component = (link != null) ? LinkCard : Card;
  const to = `/catalog/sample/${id}`;
  return h(component, {className: 'sample-card', to}, [
    h('h4.name', name),
    h('div.location-name', location_name),
    h.if(material != null)('div.material', material)
  ]);
};

export {SampleCard};
