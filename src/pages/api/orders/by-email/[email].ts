import type { APIRoute } from 'astro';
import { query } from '../../../../lib/db';

/**
 * GET /api/orders/by-email/:email
 *
 * Public endpoint (no auth) used by the customer panel at /panel.
 * Returns customer info + all orders for a given email.
 */
export const GET: APIRoute = async (context) => {
  try {
    const { email } = context.params;
    if (!email) {
      return new Response(JSON.stringify({ error: 'Email required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const decodedEmail = decodeURIComponent(email);

    // Find customer
    const customerResult = await query(
      'SELECT id, name, email, phone, created_at FROM customers WHERE email = $1',
      [decodedEmail]
    );

    if (customerResult.rows.length === 0) {
      return new Response(JSON.stringify({ customer: null, orders: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const customer = customerResult.rows[0];

    // Find orders
    const ordersResult = await query(
      `SELECT id, plan_type, amount, status, created_at, updated_at
       FROM orders WHERE customer_id = $1
       ORDER BY created_at DESC`,
      [customer.id]
    );

    return new Response(JSON.stringify({
      customer,
      orders: ordersResult.rows,
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error in by-email lookup:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
