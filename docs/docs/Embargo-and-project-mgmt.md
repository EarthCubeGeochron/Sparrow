---
id: embargo-mgmt
title: Embargo and project management
sidebar_label: Embargo and project management
---

## General principles of data availability

1. Sparrow has two complementary goals: A) support geochronology labs’ efforts to organize and contextualize their analytical data archives and B) make geochronological data findable, accessible, interoperable, and reusable (FAIR) by facilitating their easy and fast pipelining from internal lab workflows to open data portals that support the diverse communities that collect and use geochronological data.
2. Embargoes in Sparrow serve these goals by A) enabling all geochronological data to be fully integrated with Sparrow capabilities, B) protecting the first-use rights of geochronology labs, clients, and collaborators to privately analyze and prepare data prior to publication or other forms of public release, and C) creating clearly defined pathways and norms to openly release geochronological data.
3. Because geochronological labs work with a variety of collaborators and clients, public and private, Sparrow supports multiple levels of data restriction, from full public to full private, with temporary embargoes the default option.

## Embargo Design and Policy

Embargoes in Sparrow can be set and enforced at several levels, with settings made at higher granularity (higher in list) overriding more generic settings (lower in list):

1. Individual analytical sessions
2. Individual samples
3. Individual projects that are defined in Sparrow
4. A geochronology lab’s entire archive

The Sparrow embargo design supports several levels of protection:

**Public:** all indexed data and metadata accessible. This level of data is fully FAIR, reproducible, and compatible with policy for NSF and other public science agencies.

**Temporary:** For temporarily embargoed datasets, basic metadata are publicly viewable, but the analytical datasets themselves are not. Basic metadata include current end date of embargo, lab identity, and researchers’ names. Geospatial coordinates are normally but not always included in basic metadata. Standard tools for searching public webfacing servers supported by Sparrow can return basic metadata for embargoed data. No age estimates or analytical data will be returned for embargoed data. Temporary embargoes end when trigger conditions are met. (This is the default for all data if no embargo policy is not set.)

**Private:** No information exposed to unauthorized users. This level is appropriate only for data where commercial contracts preclude outside disclosure.

## Basic design: configurable, lab-controlled embargo

Sparrow’s core contains tools for labs to set permanent or expiring embargos for their data and and limit access based on that policy. Embargoes are optional and the default option is a 2-year term. For data to be embargoed, a **Sparrow administrator** (usually a member of the geochronology lab where the original measurements were made) must activate a global, project, or sample/session level embargo. The key parameters for the basic embargo system are “embargo duration” and “embargo level”.

## Embargo management

The **Sparrow administrator** sets embargo and can adjust it currently. To do this... <!-- Add in some additional instructions here. -->

## Project management

New information such as paper titles and additional samples can be added to projects using new tools. <!-- Add some information on the new tools for these edits from Casey. -->
