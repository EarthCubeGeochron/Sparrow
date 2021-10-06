import React from "react";
import Link from "next/link";
import h from "@macrostrat/hyper";
import { DarkModeButton, GetAppButton } from "./buttons";

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
  { href: "/docs", label: "Documentation" },
  { href: "/guides", label: "Guides" },
  { href: "/guides/get-started", label: "Get started!" },
  h("li.spacer"),
  h("li", null, h(DarkModeButton, { large: false }))
];

const guideLinks: Links = [
  { href: "/guides/getting-started", label: "Getting started" },
  { href: "/guides/motivation-and-design", label: "Motivation and design" },
  {
    href: "/guides/schema",
    label: "Schema and Importing data",
    children: [
      { href: "/guides/schema/importers", label: "Importers" },
      {
        href: "/guides/schema/wiscsims-example",
        label: "WiscSims Importer Example"
      }
    ]
  },
  {
    href: "/guides/tutorials",
    label: "User Tutorials",
    children: [
      {
        href: "/guides/tutorials/metadata-importer",
        label: "Metadata Importer"
      },
      { href: "/guides/tutorials/datascience", label: "Data science" },
      { href: "/guides/tutorials/views-and-tables", label: "Views and Tables" },
      {
        href: "/guides/tutorials/frontend-visualizations",
        label: "Frontend Visualization"
      },
      {
        href: "/guides/tutorials/custom-commands",
        label: "Adding Custom Commands"
      },
      { href: "/guides/tutorials/map-views", label: "Map Views" },
      { href: "/guides/tutorials/docker-ubuntu", label: "Docker for Ubuntu" }
    ]
  },
  { href: "/guides/embargo", label: "Embargo" },
  {
    href: "/guides/integrations",
    label: "Integrations",
    children: [
      {
        href: "/guides/integrations/postgresql-client",
        label: "PostgreSQL Client"
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
        label: "Lab Implementations"
      }
    ]
  }
];

const aboutLinks: Links = [
  { href: "/about", label: "Motivation" },
  { href: "/about/implementations", label: "Implementations" },
  { href: "/about/presentations", label: "Presentations" }
  // { href: '/about/features', label: "Features"}
];

const docsLinks: Links = [
  { href: "/docs", label: "Getting started" },
  { href: "/docs/windows", label: "Sparrow on Windows" },
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
      { href: "/docs/frontend/data-input-form", label: "Data Input Form" },
      { href: "/docs/frontend/frames", label: "Extensions and Frames" }
    ]
  },
  {
    href: "/docs/development",
    label: "Development",
    children: [
      { href: "/docs/development/sparrow-cli", label: "Sparrow CLI" },
      { href: "/docs/development/backend-plugins", label: "Backend Plugins" },
      { href: "/docs/development/frontend-plugins", label: "Frontend Plugins" },
      {
        href: "/docs/development/local-development",
        label: "Local development"
      }
    ]
  },
  {
    href: "/docs/misscellaneous",
    label: "Misscellaneous",
    children: [
      {
        href: "/docs/misscellaneous/linux-permissions",
        label: "Linux Permissions"
      },
      { href: "/docs/misscellaneous/docker-issues", label: "Docker Issues" },
      {
        href: "/docs/misscellaneous/trouble-shooting",
        label: "Trouble Shooting"
      }
    ]
  }
];

export { navLinks, aboutLinks, docsLinks, guideLinks };
