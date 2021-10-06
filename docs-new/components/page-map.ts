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
  { href: "/guides/motivation-and-design", label: "Motivation and design" },
  {
    href: "/guides/schema",
    label: "Schema and importing data",
    children: [{ href: "/guides/schema/importers", label: "Importers" }]
  },
  {
    href: "/guides/tutorials",
    label: "User Tutorials",
    children: [
      { href: "/guides/tutorials/datascience", label: "Data science" },
      { href: "/guides/tutorials/views-and-tables", label: "Views and tables" },
      {
        href: "/guides/tutorials/frontend-visualizations",
        label: "Frontend visualization"
      },
      {
        href: "/guides/tutorials/custom-commands",
        label: "Adding custom commands"
      },
      { href: "/guides/tutorials/map-views", label: "Map views" },
      { href: "/guides/tutorials/docker-ubuntu", label: "Docker for ubuntu" }
    ]
  },
  { href: "/guides/embargo", label: "Embargo" },
  {
    href: "/guides/integrations",
    label: "Integrations",
    children: [
      {
        href: "/guides/integrations/postgresql-client",
        label: "PostgreSQL client"
      },
      {
        href: "/guides/integrations/qgis",
        label: "QGIS"
      }
    ]
  },
  {
    href: "/guides/resources",
    label: "Resources",
    children: [
      { href: "/guides/resources/presentations", label: "Presentations" },
      {
        href: "/guides/resources/lab-implementations",
        label: "Lab implementations"
      }
    ]
  }
];

const aboutLinks: Links = [
  { href: "/about", label: "Motivation" },
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
      }
    ]
  },
  {
    href: "/docs/core",
    label: "Core application",
    children: [
      { href: "/docs/core/cli", label: "Command-line interface" },
      { href: "/docs/core/server-config", label: "Server configuration" },
      { href: "/docs/core/plugins", label: "Plugins" },
      { href: "/docs/core/extensions", label: "Extensions" }
    ]
  },
  { href: "/docs/database", label: "Database" },
  {
    href: "/docs/development/frontend",
    label: "Frontend",
    children: [
      { href: "/docs/frontend/data-input-form", label: "Data input form" },
      { href: "/docs/frontend/frames", label: "Extensions and frames" }
    ]
  },
  {
    href: "/docs/development",
    label: "Development",
    children: [
      { href: "/docs/development/sparrow-cli", label: "Sparrow CLI" },
      {
        href: "/docs/development/local-development",
        label: "Local development"
      }
    ]
  },
  { href: "/docs/windows", label: "Sparrow on windows" },
  {
    href: "/docs/misscellaneous",
    label: "Miscellaneous",
    children: [
      {
        href: "/docs/misscellaneous/linux-permissions",
        label: "Linux permissions"
      },
      { href: "/docs/misscellaneous/docker-issues", label: "Docker issues" },
      {
        href: "/docs/misscellaneous/trouble-shooting",
        label: "Trouble shooting"
      }
    ]
  }
];

export { navLinks, aboutLinks, docsLinks, guideLinks };
