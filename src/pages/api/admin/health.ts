import type { APIRoute } from 'astro';

/**
 * GET /api/admin/health
 *
 * Health check endpoint. In production, fails loudly if ADMIN_PASSWORD
 * or AUTH_SECRET are still set to default values.
 */
export const GET: APIRoute = async () => {
  const adminPassword = import.meta.env.ADMIN_PASSWORD || '';
  const authSecret = import.meta.env.AUTH_SECRET || '';
  const isProd = import.meta.env.PROD;

  const warnings: string[] = [];

  if (isProd) {
    if (!adminPassword) {
      warnings.push('ADMIN_PASSWORD is not set');
    }
    if (!authSecret || authSecret === 'tpt-admin-secret-change-me') {
      warnings.push('AUTH_SECRET is not set or still using default');
    }
  }

  const healthy = warnings.length === 0;

  return new Response(JSON.stringify({
    status: healthy ? 'healthy' : 'degraded',
    service: 'Trust Para Todos API',
    version: '1.0.0',
    production: isProd,
    warnings: warnings.length > 0 ? warnings : undefined,
  }), {
    status: healthy ? 200 : 503,
    headers: { 'Content-Type': 'application/json' },
  });
};
