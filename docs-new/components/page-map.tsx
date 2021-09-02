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

const navLinks: Links = [
  { href: "/about", label: "About" },
  { href: "/docs", label: "User guide" },
  h("li.spacer"),
  h("li", null, h(GetAppButton)),
  h("li", null, h(DarkModeButton)),
];

const aboutLinks: Links = [
  { href: "/about", label: "Motivation" },
  // { href: '/about/features', label: "Features"}
  { href: "/about/pricing", label: "Pricing + evaluation" },
  { href: "/about/interop", label: "Openness + interoperability" },
  { href: "/about/features", label: "Features + comparisons" },
  { href: "/about/gallery", label: "Gallery" },
  { href: "/about/changelog", label: "Version history" },
  { href: "/about/roadmap", label: "Roadmap" },

  //{ href: '/about/get-involved', label: "Get involved" }
  //{ href: '/about/contact', label: "Contact"}
];

const userGuideLinks: Links = [
  { href: "/docs", label: "Getting started" },
  {
    href: "/docs/projects",
    label: "Projects",
    children: [
      {
        href: "/docs/projects/new-project",
        label: "Project creation options",
        shortLabel: "Creation options",
      },
      {
        href: "/docs/projects/file-format",
        label: "Project file format",
        shortLabel: "File format",
      },
    ],
  },
  { href: "/docs/map-interface", label: "Map interface" },
  { href: "/docs/data-types", label: "Data types" },
  { href: "/docs/topology", label: "Topology" },
  { href: "/docs/basemaps", label: "Basemaps" },
  { href: "/docs/tethered-mode", label: "Tethered mode" },
  { href: "/docs/reporting-bugs", label: "Reporting bugs" },
];

export { navLinks, aboutLinks, userGuideLinks };
