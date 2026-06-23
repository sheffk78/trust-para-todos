import type { APIRoute } from 'astro';
import { clearSessionCookie } from '../../../lib/auth';

export const POST: APIRoute = async (context) => {
  clearSessionCookie(context);
  return new Response(JSON.stringify({ success: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};

// Also accept GET for simpler browser-based logout
export const GET: APIRoute = async (context) => {
  clearSessionCookie(context);
  return context.redirect('/admin/login');
};
