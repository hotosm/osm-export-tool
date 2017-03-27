const path = require('path');

module.exports = {
  entry: './app/hdx/base.js',
  output: {
    path: path.resolve(__dirname, 'static','ui','js'),
    filename: 'bundle.js'
  },
  //devtool: 'inline-source-map',
  module: {
    loaders: [
      {
        test: /app\/.*\.jsx?$/,
        exclude: [/node_modules/],
        loader: 'babel-loader',
        query: {
          presets: ["es2015","react","stage-0"]
        }
      },
      {
        test: /app.*\.css$/,
        loader: 'style-loader'
      }, {
        test: /app.*\.css$/,
        loader: 'css-loader',
        query: {
          modules: true,
          localIdentName: '[name]__[local]___[hash:base64:5]'
        }
      }
    ]
  }
};
