import React from "react";
import classnames from "classnames";
import styles from "./styles.module.scss";
import Mdx from "../text/index-text.mdx";
import BasePage from "../components/base-page";

const features = [
  {
    title: <>Manage your geochemical data</>,
    description: (
      <>
        <b>Sparrow</b> allows labs to organize analytical data and track
        project- and sample-level metadata. Its metadata management interface
        streamlines tasks such as controlling embargo, identifying and linking
        geologic and publication metadata, and generating aggregate summaries.
      </>
    ),
  },
  {
    title: <>Link to community systems</>,
    description: (
      <>
        <b>Sparrow</b> straightforwardly implements FAIR (findable, accessible,
        interoperable, reusable) data-management principles atop current data
        archives and lab analytical processes. It provides a standard API access
        layer for geochemical data produced by individual geochronology
        laboratories, which allows data to be extracted by end users and
        centralized archives.
      </>
    ),
  },
  {
    title: <>Build a web presence</>,
    description: (
      <>
        <b>Sparrow</b>'s web interface enables aggregate summaries of
        geochemical data and metadata, driven by your data archive to convey the
        scope and impact of your lab's work. Useful summaries, such as a{" "}
        <a href="sparrow.boisestate.edu">map view of sample locations</a>, are
        bundled by default.
      </>
    ),
  },
  {
    title: <>Extend and customize</>,
    description: (
      <>
        All parts of <b>Sparrow</b> can be customized. Common
        metadata-management functionality comes out of the box, but it can be
        augmented for lab-specific needs. <b>Sparrow</b> is open-source software
        that is built to be lightweight, flexible, and standards-compliant. It's
        like <a href="https://wordpress.org">Wordpress</a> for geochemical data!
      </>
    ),
  },
];

function Feature({ title, description }) {
  return (
    <div className={classnames("col", styles.feature)}>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  return (
    <BasePage
      title={`Sparrow data system`}
      description="A small and sophisticated data system for geochronology and geochemistry labs."
    >
      <header
        className={classnames("hero hero--primary", styles.heroBanner)}
      ></header>
      <main>
        {features && features.length && (
          <section className={styles.features}>
            <div className="logo-container">
              <h2>
                A small and sophisticated data system for geochronology and
                geochemistry labs.
              </h2>
              <img
                src="https://sparrow-data.org/images/sparrow-logo.png"
                width="100%"
              />
            </div>
            <div className="feature-container">
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </section>
        )}
      </main>
      <div className="container">
        <Mdx />
      </div>
    </BasePage>
  );
}

export default Home;
