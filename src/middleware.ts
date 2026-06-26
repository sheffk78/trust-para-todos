/**
 * Trust Para Todos — Astro Middleware
 * 
 * Proxies /api/* requests to the FastAPI backend if BACKEND_URL is set.
 * Handles /api/admin/*, /api/orders/*, /api/customers/* routes directly (no proxy).
 * Protects /admin/* page routes with session check.
 * Adds security headers to all responses.
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

/** Add security headers to any Response object */
function addSecurityHeaders(response: Response): Response {
  response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=(), usb=()');
  return response;
}

export const onRequest = defineMiddleware(async (context, next) => {
  const url = new URL(context.request.url);
  const pathname = url.pathname;

  // Admin page routes — protect with session check
  if (pathname.startsWith('/admin/') && pathname !== '/admin/login') {
    const session = await getSession(context);
    if (!session) {
      if (context.request.headers.get('accept')?.includes('text/html')) {
        return addSecurityHeaders(context.redirect('/admin/login'));
      }
      return addSecurityHeaders(new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      }));
    }
  }

  // Admin API routes and order/customer API routes — handle directly (not proxied)
  if (pathname.startsWith('/api/admin') || pathname.startsWith('/api/orders') || pathname.startsWith('/api/customers')) {
    const response = await next();
    return addSecurityHeaders(response);
  }

  // Only proxy /api/* calls that aren't handled above
  if (!pathname.startsWith('/api/')) {
    const response = await next();
    return addSecurityHeaders(response);
  }

  if (!BACKEND_URL) {
    return addSecurityHeaders(new Response(JSON.stringify({ 
      error: 'Backend not configured. Set BACKEND_URL env var or start the FastAPI server.'
    }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    }));
  }

  const targetUrl = `${BACKEND_URL}${pathname}${url.search}`;

  try {
    const headers = new Headers(context.request.headers);
    headers.delete('host');

    const proxyResponse = await fetch(targetUrl, {
      method: context.request.method,
      headers,
      body: ['GET', 'HEAD'].includes(context.request.method) 
        ? undefined 
        : await context.request.text(),
    });

    const responseHeaders = new Headers(proxyResponse.headers);
    responseHeaders.delete('transfer-encoding');
    responseHeaders.delete('connection');

    return addSecurityHeaders(new Response(proxyResponse.body, {
      status: proxyResponse.status,
      headers: responseHeaders,
    }));
  } catch (e) {
    return addSecurityHeaders(new Response(JSON.stringify({ error: 'Backend service unavailable' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    }));
  }
});