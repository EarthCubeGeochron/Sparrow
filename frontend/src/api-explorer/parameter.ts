/*
 * decaffeinate suggestions:
 * DS001: Remove Babel/TypeScript constructor workaround
 * DS102: Remove unnecessary code created because of implicit returns
 * DS206: Consider reworking classes to avoid initClass
 * DS207: Consider shorter variations of null checks
 * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
 */
import styled from '@emotion/styled';
import h from 'react-hyperscript';
import {Component} from 'react';
import ReactMarkdown from 'react-markdown';
import {Tag, Card, Checkbox, Button,
        Intent, InputGroup, NumericInput} from '@blueprintjs/core';
import {DatePicker} from '@blueprintjs/datetime';
import classNames from 'classnames';
import {format} from 'date-fns';

class TernaryCheckbox extends Component {
  constructor(...args) {
    {
      // Hack: trick Babel/TypeScript into allowing this before super.
      if (false) { super(); }
      let thisFn = (() => { return this; }).toString();
      let thisName = thisFn.match(/return (?:_assertThisInitialized\()*(\w+)\)*;/)[1];
      eval(`${thisName} = this;`);
    }
    this.onChange = this.onChange.bind(this);
    super(...args);
  }

  static initClass() {
    /*
    This doesn't work correctly; it's unclear why
    */
    this.defaultProps = {
      onChange() {}
    };
    this.prototype.options = [null, true, false];
  }
  onChange() {
    const {onChange, value} = this.props;
    const ix = this.options.indexOf(value);
    const newIx = (ix+1)%3;
    return onChange(this.options[newIx]);
  }

  render() {
    const {value} = this.props;
    const ix = this.options.indexOf(value);
    return h(Checkbox, {
      onChange: this.onChange,
      checked: ix === 1,
      indeterminate: ix === 0
    });
  }
}
TernaryCheckbox.initClass();

class DateInput extends Component {
  render() {
    const {onChange} = this.props;
    return h(DatePicker, {onChange});
  }
}

class InputForType extends Component {
  render() {
    let onChange;
    let {type, value, update, name} = this.props;
    const updateSt = function(val){
      let cset;
      if ((val == null) || (val === "")) {
        cset = {$unset: [name]};
      } else {
        cset = {[name]: {$set: val}};
      }
      return update(cset);
    };

    if (type === 'bool') {
      return h(TernaryCheckbox, {
        onChange: val=> {
          return update({[name]: {$set: val}});
        },
        value
      });
    }
    if (type === 'str') {
      if (value == null) { value = ""; }
      onChange = evt => updateSt(evt.target.value);
      return h(InputGroup, {
        id: "text-input",
        placeholder: "string",
        value,
        onChange
      });
    }
    if (type === 'int') {
      const onValueChange = (num, string) => updateSt(string);
      if (value == null) { value = ""; }
      return h(NumericInput, {
        id: "text-input",
        placeholder: "integer",
        value,
        onValueChange
      });
    }
    if (type === 'date') {
      onChange = function(v){
        const formattedDate = format(v, "YYYY-MM-DD");
        return updateSt(formattedDate);
      };
      return h(DateInput, {onChange});
    }
    return null;
  }
}

const STag = styled(Tag)`\
margin-right: 0.3em;
margin-bottom: 0.2em;\
`;

const DeleteButton_ = props => h(Button, {icon: 'cross', intent: Intent.DANGER, minimal: true, small: true, ...props});

const DeleteButton = styled(DeleteButton_)`\
position: absolute;
top: 5px;
right: 5px;\
`;

const BaseParameter = function(props){
  let onClick;
  let {name, default: defaultArg,
   description, expand, type,
   value, update,
   usage, expanded, className} = props;

  className = classNames(className, 'argument', {expanded});

  if (usage != null) {
    usage = h(ReactMarkdown, {source: usage});
  }

  if (type === 'boolean') {
    type = 'bool';
  }
  if (type === 'datetime') {
    type = 'date';
  }

  const attrs = [
    h(STag, type)
  ];

  if ((description != null) && description.startsWith("Column")) {
    description = null;
    const intent = Intent.SUCCESS;
    attrs.push(h(Tag, {intent}, "column"));
  }

  if (defaultArg != null) {
    attrs.push(h(Tag, `default: ${defaultArg}`));
  }

  if ((expand != null) && !expanded) {
    onClick = () => {
      return expand(name);
    };
  }

  let details = null;
  if (expanded) {
    details = h('div.details', [
      usage,
      h(InputForType, {type, value, update, name})
    ]);
  }

  let deleteButton = null;
  if (value != null) {
    deleteButton = h(DeleteButton, {
      onClick() {
        return update({$unset: [name]});
      }
    });
  }

  return h(Card, {
    interactive: !expanded,
    key: name,
    className,
    onClick
  }, [
    h('div.top', [
      h('h5.name', name),
      h('div.attributes', attrs)
    ]),
    (description != null) ? h('p.description', description) : undefined,
    details,
    deleteButton
  ]);
};

const Parameter = styled(BaseParameter)`\
margin-bottom: 1em;
margin-right: 1em;
transition: width 0.5s;
position: relative;
flex-grow: ${function(p){ if (p.type === 'string') { return '2'; } else { return '1'; } }};\
`;

export {Parameter};
