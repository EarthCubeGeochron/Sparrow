import h from 'react-hyperscript'
import {Component} from 'react'
import {StatefulComponent} from '@macrostrat/ui-components'
import {Button, Dialog, Intent, Classes} from '@blueprintjs/core'
import classNames from 'classnames'
import './main.styl'

class LoginFormInner extends Component
  render: ->
    className = classNames(Classes.INPUT, "bp3-large")
    {data, onChange} = @props
    h 'form.login-form', [
      h 'input', {
        type: "text",
        name: 'username'
        value: data.username
        onChange
        className,
        placeholder: "Username"
      }
      h 'input', {
        type: "password",
        name: 'password'
        value: data.password
        onChange
        className,
        placeholder: "Password"
      }
    ]

class LoginForm extends StatefulComponent
  constructor: ->
    super arguments...
    @state = {
      data: {username: "", password: ""}
    }

  isValid: =>
    {data} = @state
    {username, password} = data
    return false unless username?
    return false unless password?
    return false if password.length < 4
    return false if username.length < 4
    return true

  render: ->
    {isOpen, onClose} = @props
    {data} = @state

    onChange = (e)=>
      return unless e.target?
      @updateState {data: {[e.target.name]: { $set: e.target.value }}}

    title = "Login"
    h Dialog, {isOpen, title, onClose, icon: 'log-in'}, [
      h 'div', {className: Classes.DIALOG_BODY}, [
        h LoginFormInner, {data, onChange}
      ]
      h 'div', {className: Classes.DIALOG_FOOTER}, [
        h 'div', {className: Classes.DIALOG_FOOTER_ACTIONS}, [
          h Button, {
            intent: Intent.PRIMARY,
            large: true,
            disabled: not @isValid()}, 'Login'
        ]
      ]
    ]


export {LoginForm}
