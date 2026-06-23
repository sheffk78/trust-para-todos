import type { APIRoute } from 'astro';
import { getCustomersList, safePage, safeLimit } from '../../../lib/db';
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
    const page = safePage(context.url.searchParams.get('page'));
    const limit = safeLimit(context.url.searchParams.get('limit'));
    const offset = (page - 1) * limit;

    const { customers, total } = await getCustomersList({ search, limit, offset });

    return new Response(JSON.stringify({ customers, total, page, limit }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error fetching customers:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
