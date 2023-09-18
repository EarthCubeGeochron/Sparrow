export const apiBaseURL = import.meta.env.API_BASE_URL ?? "/";

let defaultTitle = import.meta.env.SPARROW_LAB_NAME;
if (defaultTitle == "") defaultTitle = null;
defaultTitle ??= "Test Lab";

export const siteTitle = defaultTitle;

export const mapboxAPIToken = import.meta.env.MAPBOX_API_TOKEN;
