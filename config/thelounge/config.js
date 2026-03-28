"use strict";

module.exports = {
  // Public mode: false = require login, true = single shared session
  public: false,

  // Web server port
  port: 9000,

  // Bind to all interfaces (Docker)
  host: "0.0.0.0",

  // Theme
  theme: "default",

  // Pre-fill network settings for new users
  defaults: {
    name: "Fleet IRC",
    host: "host.docker.internal",
    port: 6667,
    tls: false,
    rejectUnauthorized: false,
    nick: "human",
    username: "human",
    realname: "Fleet Operator",
    join: "#fleet,#alerts,#reviews",
  },

  // Message storage
  messageStorage: ["sqlite"],

  // Search (requires sqlite storage)
  searchEnabled: true,

  // File uploads
  fileUpload: {
    enable: true,
    maxFileSize: 10240, // 10 MB
  },

  // Prefetch link previews (shows GitHub PR titles inline)
  prefetch: true,
  prefetchStorage: true,
  prefetchMaxImageSize: 2048,

  // Log raw IRC messages for debugging
  debug: {
    ircFramework: false,
    raw: false,
  },
};