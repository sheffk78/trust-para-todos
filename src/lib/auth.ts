/**
 * Trust Para Todos — Admin Auth
 *
 * Simple password-based auth using a hardcoded env var (ADMIN_PASSWORD).
 * Session is managed via a signed JWT stored in a cookie.
 *
 * Rate limiting: in-memory, max 10 attempts per IP per 15-minute window.
 */
import type { APIContext } from 'astro';

const SESSION_COOKIE = 'tpt_admin_session';
const SESSION_MAX_AGE = 60 * 60 * 24; // 24 hours

// ── Rate limiter ───────────────────────────────────

interface RateLimitEntry {
  count: number;
  resetAt: number;
}

const rateLimitMap = new Map<string, RateLimitEntry>();
const RATE_LIMIT_MAX = 10;
const RATE_LIMIT_WINDOW_MS = 15 * 60 * 1000; // 15 minutes

function checkRateLimit(ip: string): boolean {
  const now = Date.now();
  const entry = rateLimitMap.get(ip);
  if (!entry || now > entry.resetAt) {
    rateLimitMap.set(ip, { count: 1, resetAt: now + RATE_LIMIT_WINDOW_MS });
    return true;
  }
  entry.count++;
  if (entry.count > RATE_LIMIT_MAX) {
    return false;
  }
  return true;
}

// ── Constant-time comparison ───────────────────────

/**
 * Compare two strings in constant time to prevent timing attacks.
 */
function constantTimeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) {
    // Still do a comparison to avoid leaking length difference via timing
    // (though length is usually visible via other channels)
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

// ── JWT helpers ────────────────────────────────────

async function createToken(email: string): Promise<string> {
  const secret = getSecret();
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const payload = btoa(JSON.stringify({
    sub: email,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + SESSION_MAX_AGE,
  }));
  const signature = await signHmac(`${header}.${payload}`, secret);
  return `${header}.${payload}.${signature}`;
}

async function verifyToken(token: string): Promise<{ sub: string } | null> {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const [header, payload, signature] = parts;
    const secret = getSecret();
    const expectedSig = await signHmac(`${header}.${payload}`, secret);
    if (!constantTimeEqual(signature, expectedSig)) return null;
    const data = JSON.parse(atob(payload));
    if (data.exp && data.exp < Math.floor(Date.now() / 1000)) return null;
    return { sub: data.sub };
  } catch {
    return null;
  }
}

async function signHmac(data: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw', encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false, ['sign']
  );
  const sig = await crypto.subtle.sign('HMAC', key, encoder.encode(data));
  return btoa(String.fromCharCode(...new Uint8Array(sig)));
}

function getSecret(): string {
  return import.meta.env.AUTH_SECRET || 'tpt-admin-secret-change-me';
}

export function getAdminPassword(): string {
  return import.meta.env.ADMIN_PASSWORD || 'admin123';
}

// ── Public API ─────────────────────────────────────

export function getClientIp(context: APIContext): string {
  const forwarded = context.request.headers.get('x-forwarded-for');
  if (forwarded) return forwarded.split(',')[0].trim();
  return 'unknown';
}

export function isRateLimited(context: APIContext): boolean {
  const ip = getClientIp(context);
  return !checkRateLimit(ip);
}

export async function login(email: string, password: string, context: APIContext): Promise<{ success: boolean; token?: string; error?: string }> {
  if (password !== getAdminPassword()) {
    // Only count failed password attempts toward rate limit
    if (isRateLimited(context)) {
      return { success: false, error: 'Demasiados intentos. Intenta de nuevo en 15 minutos.' };
    }
    return { success: false, error: 'Contraseña incorrecta' };
  }
  const token = await createToken(email);
  return { success: true, token };
}

export async function getSession(context: APIContext): Promise<{ email: string } | null> {
  const cookie = context.cookies.get(SESSION_COOKIE);
  if (!cookie?.value) return null;
  const payload = await verifyToken(cookie.value);
  if (!payload) return null;
  return { email: payload.sub };
}

export function setSessionCookie(context: APIContext, token: string): void {
  context.cookies.set(SESSION_COOKIE, token, {
    path: '/',
    httpOnly: true,
    secure: import.meta.env.PROD,
    sameSite: 'lax',
    maxAge: SESSION_MAX_AGE,
  });
}

export function clearSessionCookie(context: APIContext): void {
  context.cookies.set(SESSION_COOKIE, '', {
    path: '/',
    httpOnly: true,
    secure: import.meta.env.PROD,
    sameSite: 'lax',
    maxAge: 0,
  });
}

export async function requireAdmin(context: APIContext): Promise<{ email: string } | null> {
  const session = await getSession(context);
  if (!session) return null;
  return session;
}
