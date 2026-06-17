import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import node from '@astrojs/node';

import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  output: 'server',
  adapter: cloudflare(),
  integrations: [react()],
  site: 'https://trustparatodos.com',
  server: { port: 3000, host: true }
});