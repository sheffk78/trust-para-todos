/**
 * Trust Para Todos — Astro Middleware
 * 
 * Proxies /api/* requests from the Astro frontend to the FastAPI backend.
 * In development: proxies to http://localhost:8000
 * In production (Railway): proxies to internal backend service
 * 
 * Set BACKEND_URL env var to control the target.
 * If not set, the API calls are passed through (same-service mode).
 */
import { defineMiddleware } from 'astro/middleware';

const BACKEND_URL = import.meta.env.BACKEND_URL || '';

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.request.url);

  // Only proxy /api/* calls
  if (!url.pathname.startsWith('/api/')) {
    return next();
  }

  if (!BACKEND_URL) {
    // In development or when backend is on the same service,
    // return a helpful error so developers know to start the backend
    return new Response(JSON.stringify({ 
      error: 'Backend not configured. Set BACKEND_URL env var or start the FastAPI server.'
    }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const targetUrl = `${BACKEND_URL}${url.pathname}${url.search}`;

  try {
    const headers = new Headers(context.request.headers);
    headers.delete('host');

    const response = await fetch(targetUrl, {
      method: context.request.method,
      headers,
      body: ['GET', 'HEAD'].includes(context.request.method) 
        ? undefined 
        : await context.request.text(),
    });

    // Clone response headers (Content-Type, etc.)
    const responseHeaders = new Headers(response.headers);
    // Remove hop-by-hop headers
    responseHeaders.delete('transfer-encoding');
    responseHeaders.delete('connection');

    return new Response(response.body, {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (e) {
    return new Response(JSON.stringify({ error: 'Backend service unavailable' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
});