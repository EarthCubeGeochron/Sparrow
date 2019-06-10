---
title: >
  Sparrow: a geochronology laboratory data management system
  supporting interchange between geochronology laboratories
author: D.P. Quinn, S.E. Peters
---

Best practices for data accessibility and archiving are a key concern within
the geochronology community. Meanwhile, robust, global age datasets are sought
as references by communities constructing time-integrated digital Earth models
at a variety of scales and time resolutions. Although essential, integrating
analytical and interpreted age data into community repositories is costly,
uncompensated work for geochronologists. **Sparrow** strives to build an
automated system to manage data integrations while preserving the link to
original laboratory data.

## Background and motivation

Currently, geochronological data is mostly handled within focused studies.
Laboratories have devised innovative systems and processes to measure
high-precision ages on a variety of isotope systems; these data underpin
studies that drive discovery in all branches of the geosciences. Within the
geochemistry community, standards for data accessibility and reporting are
essential to enable reproducibility and cross-comparability [e.g. @Renne2009].
In many cases, assumptions such as decay constants and standard ages are
revised after ages are calculated; as such, the geochronology community has
focused on building data-discovery tools emphasizing reproducibility and
recalculation [e.g. @McLean2016].

Users of age data outside the geochronology community have different
requirements for age data. Individual interpreted ages are reported
in publications to describing relevant phenomena: examples include igneous
formation ages, cooling ages, exposure ages, and radiocarbon horizon ages.
Increasingly, however, integrative models of the Earth system need large-scale
calibration for geological time. For instance, stratigraphic (e.g.
Macrostrat, @Peters2018), paleobiological (PaleoBioDB), and
paleoecology (e.g. Neatoma, @Williams2018) databases have built working models
of different facets of the Earth system, each of which has an internal
representation of time. Large sets of *interpreted* geochronology data in
geologic context can be used to cross-calibrate these models, improving our
aggregate understanding of Earth history.

Community-level approaches to systematizing and managing geochronology data
must support both reproducibility and tractable summaries for external users.
Efforts to create this data infrastructure, such as the Geochron.org project
[@McLean2016], have met with limited success, archiving only a small amount
of geochronological data to date. Incorporating geochronology measurements into
a centralized repository requires conversion to an accepted format and upload.
Currently, much of this process happens manually, leading to a high workload
for researchers. Additionally, the value of the repository is only realized
with high community participation and long-term support.
These network and sustainability problems present a huge barrier to uptake
of a community-wide data system.

**Sparrow**, a new open-source software component funded by NSF EarthCube^[1],
attempts to improve the situation by building a modern data system
within individual labs, instead of at the community level. High-level data-management
tools can benefit labs by streamlining sample management workflows. However,
**Sparrow** decouples data management from analytical procedures, allow labs to
maintain complete control of their measurement and data-reduction workflows
while automating dissemination and contextualization of results.

## Design

At its core, **Sparrow** is implemented within the individual
geochronology laboratories to link analytical data files to summary and contextual data.
The system can be deployed atop current, lab-
specific systems and workflows for data collection, reduction, and storage.
**Sparrow** builds a structured representation of the lab's data archive
and provides an externally accessible, standardized access layer.
This application programming interface (API) can be accessed by users including
centralized archives.

Atop this data interface, **Sparrow** bundles an extensible, web-based management
interface that streamlines tasks such as controlling data embargo,
identifying and linking geologic and publication metadata, and generating
aggregate summaries of analytical data.

Because **Sparrow** is based on a structured data store, the software straightforwardly
implements **FAIR** (findable, accessible, interoperable, reusable) data management
principles [@Wilkinson2016] for host labs. Its management interface can assist with
data-curation tasks, saving time for lab workers on internal processes. Moreover,
repositories and consumers can "pull" data from a standard, discoverable API,
shifting the onus of data aggregation onto repositories and consumers, and
eliminating the need for labs to manually push data to the community.

## Technical architecture

**Sparrow** is designed for implementation across geochronology labs that
specialize in a variety of isotope systems, analytical methods, and
data-reduction techniques. As such, it is built to be customizable across labs.
Additionally, it is designed for easy implementation using a containerized
architecture. Its lightweight, flexible, and standards-compliant software stack
is designed for extensibility and sustainability.

At its core, **Sparrow** is a fairly standard web application that includes a
database engine, web server, and user-facing website.
The database engine, powered by [PostgreSQL](https://postgresql.org), stores
analytical data and metadata.
The backend server, implemented in [Python](https://www.python.org), interfaces
with the database and handles
user authentication, data filtering, and the publicly accessible API. The
web frontend provides interfaces for data management, embargo control,
and rich data-driven aggregates of lab data such as web maps, age summaries,
and other lab-specific views.

### Database schema

The **Sparrow** database schema is designed to handle a wide range of
analytical geochemical information. The schema can incorporate anything that is
organized into a sequence of spatially- or time-resolved analyses of each
fraction of sample. The data shape expected by **Sparrow** is similar to that
implemented by other, more focused tools such as **ETRedux** and **PyChron**.
The **Sparrow** database also incorporates a generic framework
for project, sample, geologic context, and
publication metadata; this data store allows many aspects of the measurement
lifecycle to be tracked. The data store can be customized by adding new
method-specific tables and views; for instance, plugins for tracking
spatially-resolved analyses are planned to support in-situ techniques such as
SIMS and LA-ICP-MS.

### Import scripts

Data is incorporated into **Sparrow** using import scripts that are customized
to each analytical data format. Both machine-readable formats (e.g. PyChron
JSON and ETRedux XML) and tabular data summaries (e.g. Excel data-reduction
output) are supported. Import scripts can be written in any language, but
Python helper libraries packaged with **Sparrow** provide common mechanisms for
change detection and data-file linking. Since import is automatic and original
data files are preserved, data can be imported progressively without worry
about losing connection to the raw analytical information.

### Web server

The Python-based web server implements a public API atop the **Sparrow** database.
It manages authentication, filtering, and embargo, and provides
a command-line management interface. This core is intentionally lightweight
and simplistic, with most of the logic encapsulated in ~500 lines of Python code.
Most of the application's structure is represented directly in the database,
which allows interoperability with external tools.

### Frontend interface

The frontend interface to **Sparrow**, implemented as
a [React](https://reactjs.org) Javascript application, is decoupled from the
backend but provides a default set of user-interface components that enable
metadata management and display. It is modular and pluggable, so that different
views can be implemented for different labs. For instance, age spectrum views
are available for detrital zircon datasets and step heating curves can be
plotted for Ar/Ar measurements.



### Containerization

## Implementation progress


it is built to be lightweight, flexible, and standards-compliant.

Sparrow is now being deployed atop several distinct data-reduction pipelines
at laboratories specializing in U-Pb, $^{40}$Ar/$^{39}$Ar, and cosmogenic nuclide dating.
Where implemented, the software will automate the incorporation of lab-curated
geochemical data into synthesis and archival facilities.

[1](https://sparrow-data.org)
