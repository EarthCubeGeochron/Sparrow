export const apiBaseURL = import.meta.env.VITE_API_BASE_URL ?? "/";

let defaultTitle = import.meta.env.VITE_SPARROW_LAB_NAME;
if (defaultTitle == "") defaultTitle = null;
defaultTitle ??= "Test Lab";

export const siteTitle = defaultTitle;

export const mapboxAPIToken = import.meta.env.VITE_MAPBOX_API_TOKEN;
