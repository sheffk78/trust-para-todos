import type { APIRoute } from 'astro';
import { getOrdersList, safePage, safeLimit } from '../../../lib/db';
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
    const search = context.url.searchParams.get('search') || undefined;
    const status = context.url.searchParams.get('status') || undefined;
    const plan = context.url.searchParams.get('plan') || undefined;
    const page = safePage(context.url.searchParams.get('page'));
    const limit = safeLimit(context.url.searchParams.get('limit'));
    const offset = (page - 1) * limit;

    const { orders, total } = await getOrdersList({ search, status, plan, limit, offset });

    return new Response(JSON.stringify({ orders, total, page, limit }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error fetching orders:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
