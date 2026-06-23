import type { APIRoute } from 'astro';
import { getDashboardStats } from '../../../lib/db';
import { requireAdmin } from '../../../lib/auth';

export const GET: APIRoute = async (context) => {
  const session = await requireAdmin(context);
  if (!session) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  try {
    const stats = await getDashboardStats();
    return new Response(JSON.stringify(stats), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error fetching dashboard stats:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
