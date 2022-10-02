export const apiBaseURL = process.env.API_BASE_URL ?? "/";

let defaultTitle = process.env.SPARROW_LAB_NAME;
if (defaultTitle == "") defaultTitle = null;
defaultTitle ??= "Test Lab";

export const siteTitle = defaultTitle;

export const mapboxAPIToken = process.env.MAPBOX_API_TOKEN;
