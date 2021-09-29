import BasePage from "./base";
import h from "@macrostrat/hyper";
import { Nav, BottomNav } from "../nav";
import { aboutLinks, docsLinks } from "../page-map";

const NavPage = ({ children, links }) =>
  h(BasePage, { className: "section-page" }, [
    h(Nav, { className: "section-nav", links, showNextPrev: true }),
    h("div.section-main", [
      h("div.section-content", children),
      h(BottomNav, { links }),
    ]),
  ]);

const AboutPage = ({ children }) => h(NavPage, { children, links: aboutLinks });

const DocsPage = ({ children }) => h(NavPage, { children, links: docsLinks });

export { BasePage, AboutPage, DocsPage };
