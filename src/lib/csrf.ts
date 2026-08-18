/**
 * Trust Para Todos — CSRF Protection (Double-Submit Cookie Pattern)
 *
 * On every page load the middleware sets a csrf_token cookie with a random
 * token.  Server-rendered pages embed the same token as a hidden form field
 * (or data attribute).  POST endpoints compare the token sent in the
 * request body / header against the cookie value.
 *
 * Usage in Astro pages (frontmatter):
 *   import { getCsrfToken } from '../lib/csrf';
 *   const csrfToken = getCsrfToken(context);
 *
 * Usage in forms:
 *   <input type="hidden" name="csrf_token" value={csrfToken} />
 *
 * Usage in API endpoints:
 *   import { validateCsrfRequest } from '../lib/csrf';
 *   if (!validateCsrfRequest(context, body)) { return csrfError(); }
 */
import type { APIContext } from 'astro';

const CSRF_COOKIE = 'tpt_csrf_token';
const CSRF_HEADER = 'x-csrf-token';
const CSRF_FIELD = 'csrf_token';

// ── Token generation ────────────────────────────────

function generateToken(): string {
  const bytes = new Uint8Array(32);
  crypto.getRandomValues(bytes);
  return btoa(String.fromCharCode(...bytes)).replace(/[+/=]/g, '').slice(0, 32);
}

// ── Cookie helpers ───────────────────────────────────

export function setCsrfCookie(context: APIContext, token: string): void {
  context.cookies.set(CSRF_COOKIE, token, {
    path: '/',
    httpOnly: false, // Must be readable by client-side JS for double-submit
    secure: import.meta.env.PROD,
    sameSite: 'lax',
    maxAge: 60 * 60 * 24, // 24 hours
  });
}

export function getCsrfTokenFromCookie(context: APIContext): string | null {
  const cookie = context.cookies.get(CSRF_COOKIE);
  return cookie?.value || null;
}

// ── Public API ───────────────────────────────────────

/**
 * Get or create a CSRF token for the current request.
 * Call this in Astro page frontmatter to inject the token into forms.
 */
export function getCsrfToken(context: APIContext): string {
  const existing = getCsrfTokenFromCookie(context);
  if (existing) return existing;

  const token = generateToken();
  setCsrfCookie(context, token);
  return token;
}

/**
 * Validate CSRF token from a JSON body field.
 * Call this in API endpoints after parsing the JSON body.
 */
export function validateCsrfToken(bodyToken: string | undefined, context: APIContext): boolean {
  if (!bodyToken) return false;
  const cookieToken = getCsrfTokenFromCookie(context);
  if (!cookieToken) return false;
  return constantTimeEqual(bodyToken, cookieToken);
}

/**
 * Validate CSRF from either header or body. Works for form-encoded and JSON.
 */
export function validateCsrfRequest(context: APIContext, body?: Record<string, unknown>): boolean {
  // Check header first
  const headerToken = context.request.headers.get(CSRF_HEADER);
  const cookieToken = getCsrfTokenFromCookie(context);
  if (!cookieToken) return false;

  if (headerToken && constantTimeEqual(headerToken, cookieToken)) {
    return true;
  }

  // Check body field
  if (body && typeof body[CSRF_FIELD] === 'string') {
    return constantTimeEqual(body[CSRF_FIELD] as string, cookieToken);
  }

  return false;
}

// ── Constant-time comparison ─────────────────────────

function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    let result = a.length ^ b.length;
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      result |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
    }
    return result === 0;
  }
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

export { CSRF_COOKIE, CSRF_HEADER, CSRF_FIELD };