import '@testing-library/jest-dom/extend-expect';

// Polyfill for TextEncoder/TextDecoder required by react-router-dom
if (typeof global.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  global.TextEncoder = TextEncoder;
  global.TextDecoder = TextDecoder;
}
