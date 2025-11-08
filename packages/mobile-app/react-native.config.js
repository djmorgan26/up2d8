const path = require('path');

module.exports = {
  project: {
    ios: {},
    android: {},
  },
  dependencies: {},
  // Point to root node_modules for monorepo setup
  reactNativePath: path.resolve(__dirname, '../../node_modules/react-native'),
};
