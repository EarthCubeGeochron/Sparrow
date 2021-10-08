import { hyperStyled } from "@macrostrat/hyper";
import { Nav, ActiveLink } from "../nav";
import Link from "next/link";
import Head from "next/head";
import { navLinks } from "../page-map";
import newGithubIssueUrl from "new-github-issue-url";
import { useRouter } from "next/router";
import { unnestLinks } from "../nav";
import { aboutLinks, docsLinks } from "../page-map";
import { analyticsHeaderScripts } from "../analytics/server";
import * as styles from "./page-layout.module.sass";

const h = hyperStyled(styles);

const GA_TRACKING_ID = process.env.GA_TRACKING_ID;

const allLinks = unnestLinks([...aboutLinks, ...docsLinks]);

function PageIssueLink() {
  const router = useRouter();
  //@ts-ignore
  const activeLink = allLinks.find((d) => d?.href == router.pathname);

  //@ts-ignore
  const pageName = activeLink?.label ?? router.pathname;

  const href = newGithubIssueUrl({
    user: "EarthCubeGeochron",
    repo: "Sparrow",
    title: `Issue with "${pageName}" page`,
    labels: ["documentation"],
  });

  return h("p", [
    "Found a problem with this page? ",
    h("a", { target: "_blank", href }, "Create an issue"),
  ]);
}

const RevisionInfo = () => {
  return null;
  // h("p.version", [
  //   `${JSON.parse(process.env.GIT_VERSION)} – ${JSON.parse(
  //     process.env.COMPILE_DATE
  //   )}`,
  //   " (",
  //   h(
  //     "a",
  //     { href: JSON.parse(process.env.GITHUB_REV_LINK) },
  //     JSON.parse(process.env.GIT_COMMIT_HASH)
  //   ),
  //   ")",
  // ]);
};

const BasePage = function (props) {
  const { children, className, ...rest } = props;

  return h("div.page", { className }, [
    <Head>
      <meta charSet="utf-8" />
      <title>Sparrow</title>
      <link rel="preconnect" href="https://fonts.gstatic.com" />
      <link
        href="https://fonts.googleapis.com/css2?family=Merriweather&family=Montserrat:wght@400;700&family=Source+Code+Pro:wght@400;700&display=swap"
        rel="stylesheet"
      />
      {analyticsHeaderScripts()}
      <link rel="icon" type="image/png" href="/favicon.png" />
      <link rel="shortcut icon" type="image/x-icon" href="/favicon.png" />
      <meta property="og:title" content="Sparrow" />
      <meta
        property="og:description"
        content="A small data system for geochemistry labs."
      />
    </Head>,
    h("div.underlay"),
    h("div.wrap", [
      h("header.page-header", [
        <div className="nav-wrap">
          <div className="header-image">
            <Link href="/">
              <img
                className="sparrow-logo"
                src="https://sparrow-data.org/images/sparrow-logo.png"
              />
            </Link>
          </div>
          <div className="nav-main">
            <ActiveLink href="/">
              <a className="page-title-link">
                <h1 className="page-title">Sparrow</h1>
              </a>
            </ActiveLink>
            <Nav links={navLinks} exactLinks={false} />
          </div>
        </div>,
      ]),
      h("div.main", [children]),
      <footer>
        <div>
          <p>
            <strong>Sparrow</strong>
          </p>
          <p>
            2018—2021, the
            <a href="https://github.com/EarthCubeGeochron">
              <em>EarthCube Geochronology</em>
            </a>{" "}
            team
          </p>
          <RevisionInfo />
        </div>

        <PageIssueLink />
      </footer>,
    ]),
  ]);
};

export default BasePage;
