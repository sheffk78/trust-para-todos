import type { APIRoute } from 'astro';
import { getCustomerDetail } from '../../../lib/db';
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
    const { id } = context.params;
    if (!id) {
      return new Response(JSON.stringify({ error: 'Customer ID required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { customer, orders, questionnaire_responses } = await getCustomerDetail(id);

    if (!customer) {
      return new Response(JSON.stringify({ error: 'Customer not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ customer, orders, questionnaire_responses }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error fetching customer detail:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
