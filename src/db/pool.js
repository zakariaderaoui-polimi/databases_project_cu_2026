// MariaDB connection handling.
//
// Conventions enforced for every connection:
//   * session time_zone '+00:00' keeps database timestamps in UTC;
//   * dateStrings preserves microsecond system timestamps without
//     converting them to JavaScript Date's millisecond precision;
//   * big integer identifiers are returned as numbers while they
//     remain safely below JavaScript's Number.MAX_SAFE_INTEGER.

import mariadb from 'mariadb';

import { config } from '../config/index.js';

export function connectionOptions({
  database = config.db.database,
  user = config.db.user,
  password = config.db.password,
  multipleStatements = false,
} = {}) {
  return {
    host: config.db.host,
    port: config.db.port,
    user,
    password,
    database,
    multipleStatements,

    dateStrings: true,
    bigIntAsNumber: true,
    insertIdAsNumber: true,
    decimalAsNumber: true,
    checkDuplicate: false,

    initSql: ["SET time_zone = '+00:00'"],

    connectTimeout: 10_000,
  };
}

export function createPool(opts = {}) {
  return mariadb.createPool({
    ...connectionOptions(opts),
    connectionLimit: opts.connectionLimit ?? 8,
    acquireTimeout: 15_000,
  });
}

export async function createConnection(opts = {}) {
  return mariadb.createConnection(connectionOptions(opts));
}