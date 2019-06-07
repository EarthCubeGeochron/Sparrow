import { Link } from "gatsby"
import PropTypes from "prop-types"
import React from "react"
import { css, jsx } from '@emotion/core'
import styled from '@emotion/styled'

const style = css`
margin-bottom: 10em;
`

const Header = ({ siteTitle }) => (
  <header>
    <div id="site-title">
      <h1 style={{ margin: 0 }}>
        <Link
          to="/"
          style={{
            textDecoration: `none`,
          }}>
          {siteTitle}
        </Link>
      </h1>
    </div>
    <nav>
      <Link to="/motivation-and-design/">Motivation and design</Link>
      <Link to="/installation/">Get started</Link>
      <a href="/python-api">Docs</a>
    </nav>
  </header>
)

Header.propTypes = {
  siteTitle: PropTypes.string,
}

Header.defaultProps = {
  siteTitle: ``,
}

export default Header
