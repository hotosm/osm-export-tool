const path = require('path');

module.exports = {
  entry: './static/ui/app/hdx/base.js',
  output: {
    path: path.resolve(__dirname, 'static','ui','build'),
    filename: 'bundle.js'
  },
  //devtool: 'inline-source-map',
  module: {
    loaders: [
      {
        test: /static\/ui\/app\/.*\.jsx?$/,
        exclude: [/node_modules/],
        loader: 'babel-loader',
        query: {
          presets: ["es2015","react","stage-0"]
        }
      },
      {
        test: /static\/ui\/app.*\.css$/,
        loader: 'style-loader'
      }, {
        test: /static\/ui\/app.*\.css$/,
        loader: 'css-loader',
        query: {
          modules: true,
          localIdentName: '[name]__[local]___[hash:base64:5]'
        }
      }
    ]
  }
};
