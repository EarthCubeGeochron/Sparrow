import h from 'react-hyperscript'
import {Button, Intent, Classes} from '@blueprintjs/core'
import classNames from 'classnames'
import './main.styl'

LoginForm = ->
  className = classNames(Classes.INPUT, "bp3-large")
  h 'div.login-form', [
    h 'input', {
      type: "text",
      className ,
      placeholder: "Username"
    }
    h 'input', {
      type: "password",
      className ,
      placeholder: "Password"
    }
  ]

export {LoginForm}
