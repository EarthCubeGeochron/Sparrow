import React, { Children } from "react";
import Link from "next/link";
import { useRouter } from "next/router";
import classNames from "classnames";
import h from "@macrostrat/hyper";
import {
  NextLinkButton,
  PrevLinkButton,
  PrevButton,
  NextButton,
} from "./buttons";
import { Links } from "./page-map";

function unnestLinks(links: Links): Links {
  let newLinks: Links = [];

  for (const link of links) {
    newLinks.push(link);
    if (link.hasOwnProperty("children")) {
      // @ts-ignore
      newLinks.push(...(link.children ?? []));
    }
  }
  return newLinks;
}

// Class to make an activeLink
const ActiveLink = function ({ children, exact = true, ...props }: any) {
  const router = useRouter();
  const child = Children.only(children);
  let className = child.props.className || "";
  const isActive = exact
    ? router.pathname === props.href
    : router.pathname.startsWith(props.href);
  className = classNames(child.props.className, { active: isActive });
  return h(Link, props, React.cloneElement(child, { className }));
};

const NavLinkItem = ({ href, label, exact }: any) => {
  return h("li", [
    h(ActiveLink, { href, exact }, [h("a.link-button", null, label)]),
  ]);
};

const NavLink = ({ children, ...rest }: any) => {
  if (children != null) {
    return h("ul", [
      h(NavLinkItem, { ...rest, exact: true, key: "a" }),
      children.map((d, i) =>
        h(NavLinkItem, { ...d, label: d.shortLabel ?? d.label, key: i })
      ),
    ]);
  }
  return h(NavLinkItem, rest);
};

function NextPrev(props: { links: Links }) {
  const links = unnestLinks(props.links);
  const { pathname } = useRouter() || {};
  if (pathname == null) {
    return null;
  }

  //@ts-ignore
  const ix = links.findIndex((d) => d.href === pathname);

  if (ix == null) {
    return null;
  }

  const prevLink = links[ix - 1];
  const nextLink = links[ix + 1];

  return h("li.nav-next-prev", [
    // @ts-ignore
    h.if(prevLink != null)(PrevButton, prevLink),
    h("span.spacer"),
    // @ts-ignore
    h.if(nextLink != null)(NextButton, nextLink),
  ]);
}

const Nav = function (props) {
  const { className, links, exactLinks, showNextPrev = false } = props;
  return h("nav", { className }, [
    h("ul", [
      links.map(function (obj) {
        if (obj.href != null) {
          obj.key = `nav-link-${obj.href}`;
          return h(NavLink, { exact: exactLinks, ...obj });
        }
        return obj;
      }),
      h.if(showNextPrev)(NextPrev, { links }),
    ]),
  ]);
};

const BottomNav = function (props: { links: Links }) {
  const links = unnestLinks(props.links);
  const { pathname } = useRouter() || {};
  if (pathname == null) {
    return null;
  }

  //@ts-ignore
  const ix = links.findIndex((d) => d.href === pathname);

  if (ix == null) {
    return null;
  }

  const prevLink = links[ix - 1];
  const nextLink = links[ix + 1];

  return h("div.bottom-links", [
    h.if(prevLink != null)(PrevLinkButton, prevLink),
    h("div.spacer"),
    h.if(nextLink != null)(NextLinkButton, nextLink),
  ]);
};

export { ActiveLink, Nav, BottomNav, unnestLinks };
