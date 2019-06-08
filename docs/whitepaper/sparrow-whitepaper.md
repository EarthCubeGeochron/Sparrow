---
title: >
  Sparrow: a geochronology laboratory data management system
  supporting interchange between geochronology laboratories
author: D.P. Quinn, S.E. Peters
---

Best practices for data accessibility and archiving are a key concern within
the geochronology community. Meanwhile, evolving time-integrated digital Earth
models must be referenced against robust, global age datasets. Increasingly,
laboratory data must be digitally accessible to a broad mosaic of data
repositories and
consumers; systems are needed to manage these integrations and automate data
archiving.

Sparrow, a new open-source software component funded by NSF EarthCube^[1],
provides a standard access layer for measurements produced by individual
geochronology laboratories. The system can be deployed atop current, lab-
specific systems and workflows for data collection, reduction, and storage. The
application programming interface (API) provided by Sparrow can be accessed by
end users [e.g. @Peters2018, @Williams2018] and centralized archives
[e.g. @McLean2016].

Sparrow also includes an extensible, web-based management overlay that
streamlines laboratory metadata management tasks such as controlling embargos,
identifying and linking geologic and publication metadata, and generating
aggregate summaries. The software straightforwardly implements **FAIR** (findable,
accessible, interoperable, reusable) data management principles [@Wilkinson2016]
for host labs; it is built to be lightweight, flexible, and standards-compliant.

Sparrow is now being deployed atop several distinct data-reduction pipelines
at laboratories specializing in U-Pb, $^{40}$Ar/$^{39}$Ar, and cosmogenic nuclide dating.
Where implemented, the software will automate the incorporation of lab-curated
geochemical data into synthesis and archival facilities.

[1](https://sparrow-data.org)
