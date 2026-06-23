import type { APIRoute } from 'astro';
import { query } from '../../../../lib/db';

/**
 * GET /api/orders/:orderId/status
 *
 * Public endpoint (no auth) used by the customer panel at /panel.
 * Returns fulfillment steps + documents for an order.
 */
export const GET: APIRoute = async (context) => {
  try {
    const { orderId } = context.params;
    if (!orderId) {
      return new Response(JSON.stringify({ error: 'Order ID required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Get fulfillment steps
    const stepsResult = await query(
      `SELECT step_name as name, status, completed_at, notes
       FROM fulfillment_steps WHERE order_id = $1
       ORDER BY created_at ASC`,
      [orderId]
    );

    // Get documents
    const docsResult = await query(
      `SELECT id, order_id, document_type as type, status, file_path, created_at
       FROM documents WHERE order_id = $1
       ORDER BY created_at ASC`,
      [orderId]
    );

    return new Response(JSON.stringify({
      steps: stepsResult.rows,
      documents: docsResult.rows,
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error in order status:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
