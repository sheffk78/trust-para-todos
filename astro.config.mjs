import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import node from '@astrojs/node';
import astroIcon from 'astro-icon';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  integrations: [react(), astroIcon()],
  site: 'https://trustparatodos.com',
  server: { port: 3000, host: true }
});
