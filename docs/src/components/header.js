import { Link } from "gatsby"
import PropTypes from "prop-types"
import React from "react"
import { css, jsx } from '@emotion/core'
import styled from '@emotion/styled'

const Navbar = styled.nav`
display: flex;
flex-direction: row;
margin: 0 -1em;
margin-top: 0.5em;
flex-grow: 2;
`;

const StyledHeader = styled.header`
display: flex;
flex-direction: row;
align-items: baseline;

a {
  text-decoration: none;
}

a:visited {
  color: inherit;
}
`

const NavLink = styled(Link)`
margin: 0.2em 1em;
`;

const NavAnchor = styled.a`
margin: 0.2em 1em;
`;


const style = css`
margin-bottom: 10em;
`

const SiteTitle = styled.div`
margin-right: 2em
`

const Header = ({ siteTitle }) => (
  <StyledHeader>
    <SiteTitle id="site-title">
      <h1 style={{ margin: 0 }}>
        <Link
          to="/"
          style={{
            textDecoration: `none`,
          }}>
          {siteTitle}
        </Link>
      </h1>
    </SiteTitle>
    <Navbar>
      <NavLink to="/motivation-and-design/">Motivation and design</NavLink>
      <NavLink to="/installation/">Installation</NavLink>
      <NavAnchor href="/python-api">Python API</NavAnchor>
    </Navbar>
  </StyledHeader>
)

Header.propTypes = {
  siteTitle: PropTypes.string,
}

Header.defaultProps = {
  siteTitle: ``,
}

export default Header
