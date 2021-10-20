import React from "react";
import Link from "next/link";
import { hyperStyled } from "@macrostrat/hyper";
import { DarkModeButton, GetAppButton } from "./buttons";
const h = hyperStyled({});
interface LinkSpec {
  href: string;
  label: string;
  shortLabel?: string;
  children?: Link[];
}

export type Link = LinkSpec | React.ReactNode;
export type Links = Link[];

// Links for the toolbar
const navLinks: Links = [
  { href: "/about", label: "About" },
  { href: "/docs/getting-started", label: "Documentation" },
  { href: "/guides", label: "Guides" },
  { href: "/docs/getting-started", label: "Get started!" },
  h("li.spacer"),
  h("li", null, h(DarkModeButton, { large: false }))
];

const guideLinks: Links = [
  {
    href: "/guides/tutorials",
    label: "User Tutorials",
    children: [
      { href: "/guides/tutorials/datascience", label: "Data science" },
      { href: "/guides/tutorials/git-github", label: "Collaborative coding" },
      { href: "/guides/tutorials/docker-ubuntu", label: "Docker for ubuntu" }
    ]
  },
  {
    href: "/guides/integrations",
    label: "Integrations",
    children: [
      {
        href: "/guides/integrations/qgis",
        label: "QGIS"
      }
    ]
  }
];

const aboutLinks: Links = [
  { href: "/about", label: "Motivation" },
  { href: "/about/sparrow-stack", label: "Tech Stack" },
  { href: "/about/implementations", label: "Implementations" },
  { href: "/about/presentations", label: "Presentations" }
];

const docsLinks: Links = [
  {
    href: "/docs/getting-started",
    label: "Getting started",
    children: [
      { href: "/docs/getting-started/create-lab", label: "Create a lab" },
      { href: "/docs/getting-started/plugins", label: "Plugins" },
      { href: "/docs/getting-started/importers", label: "Importers" },
      {
        href: "/docs/getting-started/metadata-importer",
        label: "Metadata importer"
      },
      {
        href: "/docs/getting-started/wiscsims-example",
        label: "WiscSims importer example"
      },
      {
        href: "/docs/getting-started/schema",
        label: "Schema"
      },
      { href: "/docs/getting-started/embargo", label: "Embargo" }
    ]
  },
  {
    href: "/docs/core",
    label: "Core application",
    children: [
      { href: "/docs/core/cli", label: "Command-line interface" },
      { href: "/docs/core/server-config", label: "Server configuration" },
      { href: "/docs/core/extensions", label: "Extensions" }
    ]
  },
  { href: "/docs/database", label: "Database" },
  { href: "/docs/tasks", label: "Tasks" },
  {
    href: "/docs/frontend",
    label: "Frontend",
    children: [
      { href: "/docs/frontend/map-views", label: "Map views" },
      { href: "/docs/frontend/data-input-form", label: "Data input form" },
      {
        href: "/docs/frontend/visualizations",
        label: "Frontend visualization"
      },
      { href: "/docs/frontend/frames", label: "Extensions and frames" }
    ]
  },
  {
    href: "/docs/local-development",
    label: "Local development"
  },
  { href: "/docs/windows", label: "Sparrow on windows" },
  {
    href: "/docs/misscellaneous/trouble-shooting",
    label: "Trouble shooting"
  },
  {
    href: "/docs/misscellaneous",
    label: "Miscellaneous",
    children: [
      {
        href: "/docs/misscellaneous/linux-permissions",
        label: "Linux permissions"
      },
      { href: "/docs/misscellaneous/docker-issues", label: "Docker issues" }
    ]
  }
];

export { navLinks, aboutLinks, docsLinks, guideLinks };
