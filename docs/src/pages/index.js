import React from 'react';
import classnames from 'classnames';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';
import Mdx from '../../docs/index-text.mdx'

const features = [
  {
    title: <>Manage your geochemical data</>,
    imageUrl: null,
    description: (
      <>
        <b>Sparrow</b> allows labs to organize
        analytical data and track project- and sample-level metadata.
        Its metadata management interface streamlines tasks such
        as controlling embargo, identifying and linking geologic
        and publication metadata, and generating aggregate summaries.
      </>
    ),
  },
  {
    title: <>Link to community systems</>,
    imageUrl: null,
    description: (
      <>
        <b>Sparrow</b> straightforwardly implements FAIR (findable, accessible, interoperable, reusable)
        data-management principles atop current data archives and lab analytical processes.
        It provides a standard API access layer for geochemical data produced by
        individual geochronology laboratories, which allows data to be extracted
        by end users and centralized archives.
      </>
    ),
  },
  {
    title: <>Build a web presence</>,
    imageUrl: null,
    description: (
      <>
      <b>Sparrow</b>'s web interface enables aggregate
      summaries of geochemical data and metadata, driven by your
      data archive to convey the scope and impact of your lab's work.
      Useful summaries, such as a <a href="sparrow.boisestate.edu">map view of sample locations</a>, are bundled by default.
      </>
    ),
  },
  {
    title: <>Extend and customize</>,
    imageUrl: null,
    description: (
      <>
      All parts of <b>Sparrow</b> can be customized.
      Common metadata-management functionality
      comes out of the box, but it can be augmented for lab-specific
      needs. <b>Sparrow</b> is open-source
      software that is built to be lightweight, flexible, and standards-compliant.
      It's like <a href="https://wordpress.org">Wordpress</a> for geochemical data!
      </>
    ),
  },
];

function Feature({imageUrl, title, description}) {
  const imgUrl = useBaseUrl(imageUrl);
  return (
    <div className={classnames('col col--4', styles.feature)}>
      {imgUrl && (
        <div className="text--center">
          <img className={styles.featureImage} src={imgUrl} alt={title} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`Hello from ${siteConfig.title}`}
      description="Description will go into a meta tag in <head />">
      <header className={classnames('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <div className="row">
            <div>
              <h1 className="hero__title">{siteConfig.title}</h1>
              <p className="hero__subtitle">{siteConfig.tagline}</p>
            </div>
          </div>
        </div>
      </header>
      <main>
        {features && features.length && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                <Feature>
                  <img src="/img/sparrow-logo.svg" width="300" />
                </Feature>
                {features.map((props, idx) => (
                  <Feature key={idx} {...props} />
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
      <div className="container">
        <Mdx />
      </div>
    </Layout>
  );
}

export default Home;
