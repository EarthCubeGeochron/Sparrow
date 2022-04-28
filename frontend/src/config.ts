/*
Generates site-specific configuration data
*/

// TODO: move this to a configuration file
let defaultTitle = process.env.SPARROW_LAB_NAME;
if (defaultTitle == "") defaultTitle = null;
defaultTitle ??= "Test Lab";

export const siteTitle = defaultTitle;
