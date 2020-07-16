/*
Basic functionality to bootstrap a single-page React webapp
*/

import './shared/ui-init';
import {App} from './app';
import {createElement} from 'react';
import {render} from 'react-dom';

const el = document.createElement("div")
el.id = "container"
document.body.appendChild(el)

render(createElement(App), el)
