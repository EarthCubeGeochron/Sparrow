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
  { href: "/docs", label: "User guide" },
  { href: "/get-started", label: "Get started!" },
  h("li.spacer"),
  h("li", null, h(DarkModeButton, { large: false })),
];

const guides = [
  { href: "/guides/getting-started", label: "Getting started" },
  { href: "/guides/motivation-and-design", label: "Motivation and design" },
  { href: "/guides/datascience", label: "Data science" },
  { href: "/guides/schema-imp", label: "Schema imp" },
  { href: "/guides/embargo", label: "Embargo" },
];

const aboutLinks: Links = [
  { href: "/about", label: "Motivation" },
  { href: "/about/implementations", label: "Implementations" },
  { href: "/about/presentations", label: "Presentations" },
  // { href: '/about/features', label: "Features"}
];

const docsLinks: Links = [
  { href: "/docs", label: "Getting started" },
  {
    href: "/docs/core",
    label: "Core application",
    children: [
      { href: "/docs/core/cli", label: "Command-line interface" },
      { href: "/docs/core/server-config", label: "Server configuration" },
      { href: "/docs/core/plugins", label: "Plugins" },
    ],
  },
  { href: "/docs/database", label: "Database" },
  { href: "/docs/data-import", label: "Importing data" },
  {
    href: "/docs/frontend",
    label: "Frontend",
    children: [
      //"frontend/frames",
      { href: "/frontend/data-input-form", label: "Data input form" },
      { href: "/docs/frontend/ext", label: "Extensions" },
    ],
  },
  { href: "/docs/windows", label: "Sparrow on Windows" },
  { href: "/docs/local-development", label: "Local development" },
];

export { navLinks, aboutLinks, docsLinks };
