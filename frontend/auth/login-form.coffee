import h from 'react-hyperscript'
import {Component} from 'react'
import {StatefulComponent} from '@macrostrat/ui-components'
import {AuthContext} from './context'
import {Button, Dialog, Callout, Intent, Classes} from '@blueprintjs/core'
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
  @contextType: AuthContext
  @defaultProps: {
    invalidAttempt: false
  }
  constructor: ->
    super arguments...
    @resetState()

  resetState: =>
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

  renderCallout: ->
    {invalidAttempt} = @props
    if invalidAttempt
      h Callout, {
        className: 'login-info'
        title: "Invalid credentials",
        intent: Intent.DANGER}, "Invalid credentials were provided"

  render: ->
    {doLogin, isLoggingIn: isOpen, requestLoginForm} = @context
    {data} = @state

    onChange = (e)=>
      return unless e.target?
      @updateState {data: {[e.target.name]: { $set: e.target.value }}}

    onClose = =>
      @resetState()
      requestLoginForm(false)

    title = "Login"
    h Dialog, {isOpen, title, onClose, icon: 'log-in'}, [
      h 'div.login-form-outer', {className: Classes.DIALOG_BODY}, [
        @renderCallout()
        h LoginFormInner, {data, onChange}
      ]
      h 'div', {className: Classes.DIALOG_FOOTER}, [
        h 'div', {className: Classes.DIALOG_FOOTER_ACTIONS}, [
          h Button, {
            intent: Intent.PRIMARY,
            large: true,
            onClick: =>doLogin(data),
            disabled: not @isValid()
          }, 'Login'
        ]
      ]
    ]


export {LoginForm}
