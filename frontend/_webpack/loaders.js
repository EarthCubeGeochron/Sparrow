let fontLoader = {
  loader: "file-loader",
  options: { name: "fonts/[name].[ext]" },
};

let stylusLoader = {
  loader: "stylus-relative-loader",
};

const cssModuleLoader = {
  loader: "css-loader",
  options: {
    /* CSS Module support with local scope by default
       This means that module support needs to be explicitly turned
       off with a `:global` flag
    */
    modules: {
      mode: "local",
      localIdentName: "[path][name]__[local]--[hash:base64:5]",
    },
  },
};

// Remember that, counterintuitively, loaders load bottom-to-top
const styleRules = [
  {
    test: /\.(styl|css)$/,
    use: "style-loader",
  },
  // CSS compilation supporting local CSS modules
  {
    test: /\.(styl|css)$/,
    oneOf: [
      // Match css modules (.module.(css|styl) files)
      {
        test: /\.?module\.(css|styl)$/,
        use: cssModuleLoader,
        exclude: /node_modules/,
      },
      {
        test: /\.(styl|css)$/,
        use: "css-loader",
      },
    ],
  },
  // Fallback for raw CSS and stylus from node_modules
  { test: /\.styl$/, use: stylusLoader },
];

module.exports = [
  ...styleRules,
  { test: /\.coffee$/, use: ["babel-loader", "coffee-loader"] },
  {
    test: /\.(js|jsx|ts|tsx)$/,
    use: "babel-loader",
    exclude: /node_modules/,
  },
  {
    // Rule for 'modern' javascript
    type: "javascript/auto",
    test: /\.mjs$/,
    use: [],
  },
  { test: /\.(eot|svg|ttf|woff|woff2)$/, use: [fontLoader] },
  { test: /\.md$/, use: ["html-loader", "markdown-loader"] },
  { test: /\.html$/, use: ["html-loader"] },
  {
    test: /\.(png|jpe?g|gif)$/i,
    use: [
      {
        loader: "file-loader",
        options: {
          useRelativePath: true,
        },
      },
    ],
  },
];
