import path from 'node:path';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';

export const ROOT_DIR = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  '..',
  '..',
);

dotenv.config({
  path: path.join(ROOT_DIR, '.env'),
  quiet: true,
});

export class ConfigError extends Error {}

function intFromEnv(name, fallback) {
  const value = process.env[name];

  if (value === undefined || value === '') {
    return fallback;
  }

  const parsed = Number(value);

  if (!Number.isInteger(parsed) || parsed < 0) {
    throw new ConfigError(
      `environment variable ${name} must be a non-negative integer`,
    );
  }

  return parsed;
}

export function loadConfig() {
  return Object.freeze({
    db: Object.freeze({
      host: process.env.DB_HOST || '127.0.0.1',
      port: intFromEnv('DB_PORT', 3306),
      database: process.env.DB_NAME || 'wikipedia_time_machine',
      user: process.env.DB_USER || 'wiki_user',
      password: process.env.DB_PASSWORD || '',
    }),
  });
}

export const config = loadConfig();