module.exports = function(context, options) {

  return {
    name: 'html-content',
    configureWebpack(config, isServer, utils) {
      const {getStyleLoaders} = utils

      return {
        module: {
          rules: [{
            test: /\.html$/i,
            use: 'html-loader',
          },
          {
            test: /\.styl$/i,
            use: [...getStyleLoaders(isServer, {}), 'stylus-relative-loader']
          }]
        }
      }
    },
  };
};
