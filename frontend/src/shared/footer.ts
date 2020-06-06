/*
 * decaffeinate suggestions:
 * DS102: Remove unnecessary code created because of implicit returns
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import h from 'react-hyperscript';
import {Component} from 'react';
import {Frame} from 'sparrow/frame';
import {Markdown} from '@macrostrat/ui-components';
import {InsetText} from 'app/layout';
import footerText from './footer-text.md';

const PageFooter = props => h(Frame, {id: 'pageFooter'}, (
  h(InsetText, [
    h(Markdown, {src: footerText})
  ])
)
);

export {PageFooter};
