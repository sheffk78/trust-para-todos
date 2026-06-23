/**
 * Trust Para Todos — Astro Middleware
 * 
 * Proxies /api/* requests to the FastAPI backend if BACKEND_URL is set.
 * Handles /api/admin/*, /api/orders/*, /api/customers/* routes directly (no proxy).
 * Protects /admin/* page routes with session check.
 * 
 * Public API endpoints (no auth required):
 *   - GET /api/orders/by-email/:email
 *   - GET /api/orders/:id/status
 *   - GET /api/orders/:id/documents/:docId/download
 */
import { defineMiddleware } from 'astro/middleware';
import { getSession } from './lib/auth';

const BACKEND_URL = import.meta.env.BACKEND_URL || '';

// Public API paths that don't require auth
const PUBLIC_API_PATHS = [
  '/api/orders/by-email/',
  '/api/orders/',
];

function isPublicApiPath(pathname: string): boolean {
  // Match /api/orders/:id/status and /api/orders/:id/documents/:docId/download
  const orderPattern = /^\/api\/orders\/[^\/]+\/(status|documents\/[^\/]+\/download)$/;
  return PUBLIC_API_PATHS.some(p => pathname.startsWith(p)) || orderPattern.test(pathname);
}

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.request.url);
  const pathname = url.pathname;

  // Admin page routes — protect with session check
  if (pathname.startsWith('/admin/') && pathname !== '/admin/login') {
    const session = await getSession(context);
    if (!session) {
      if (context.request.headers.get('accept')?.includes('text/html')) {
        return context.redirect('/admin/login');
      }
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }
  }

  // Admin API routes and order/customer API routes — handle directly (not proxied)
  if (pathname.startsWith('/api/admin') || pathname.startsWith('/api/orders') || pathname.startsWith('/api/customers')) {
    return next();
  }

  // Only proxy /api/* calls that aren't handled above
  if (!pathname.startsWith('/api/')) {
    return next();
  }

  if (!BACKEND_URL) {
    return new Response(JSON.stringify({ 
      error: 'Backend not configured. Set BACKEND_URL env var or start the FastAPI server.'
    }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const targetUrl = `${BACKEND_URL}${pathname}${url.search}`;

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

    const responseHeaders = new Headers(response.headers);
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
