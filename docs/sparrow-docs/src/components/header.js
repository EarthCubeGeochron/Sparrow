import { Link } from "gatsby"
import PropTypes from "prop-types"
import React from "react"
import { css, jsx } from '@emotion/core'

const style = css`
max-width 960px;
`

const Header = ({ siteTitle }) => (
  <header css={style}
    style={{
      marginBottom: `1.45rem`,
    }}
  >
    <div>
      <h1 style={{ margin: 0 }}>
        <Link
          to="/"
          style={{
            textDecoration: `none`,
          }}
        >
          {siteTitle}
        </Link>
      </h1>
    </div>
  </header>
)

Header.propTypes = {
  siteTitle: PropTypes.string,
}

Header.defaultProps = {
  siteTitle: ``,
}

export default Header
