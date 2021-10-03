import BasePage from "./base";
import h from "@macrostrat/hyper";
import { Nav, BottomNav } from "../nav";
import { aboutLinks, docsLinks, guideLinks } from "../page-map";

const NavPage = ({ children, links }) =>
  h(BasePage, { className: "section-page" }, [
    h(Nav, { className: "section-nav", links, showNextPrev: true }),
    h("div.section-main", [
      h("div.section-content", null, children),
      h(BottomNav, { links })
    ])
  ]);

const AboutPage = ({ children }) => h(NavPage, { links: aboutLinks }, children);

const DocsPage = ({ children }) => h(NavPage, { links: docsLinks }, children);

const GuidePage = ({ children }) => h(NavPage, { links: guideLinks }, children);

export { BasePage, AboutPage, DocsPage, GuidePage };
