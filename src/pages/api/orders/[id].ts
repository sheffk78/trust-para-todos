import type { APIRoute } from 'astro';
import { getOrderDetail, query } from '../../../lib/db';
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
      return new Response(JSON.stringify({ error: 'Order ID required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const { order, fulfillment_steps, documents } = await getOrderDetail(id);

    if (!order) {
      return new Response(JSON.stringify({ error: 'Order not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({ order, fulfillment_steps, documents }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error fetching order detail:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};

/**
 * PATCH /api/orders/:id
 *
 * Update order status and/or fulfillment step status.
 * Body: { status?: string, fulfillment_step?: { step_name: string, status: string, notes?: string } }
 */
export const PATCH: APIRoute = async (context) => {
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
      return new Response(JSON.stringify({ error: 'Order ID required' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Verify order exists
    const orderResult = await query('SELECT * FROM orders WHERE id = $1', [id]);
    if (orderResult.rows.length === 0) {
      return new Response(JSON.stringify({ error: 'Order not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const body = await context.request.json();
    const updates: string[] = [];
    const params: unknown[] = [];
    let paramIndex = 1;

    // Update order status
    if (body.status) {
      const validStatuses = ['pending', 'paid', 'fulfilling', 'complete'];
      if (!validStatuses.includes(body.status)) {
        return new Response(JSON.stringify({ error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      updates.push(`status = $${paramIndex++}`);
      params.push(body.status);
    }

    if (updates.length > 0) {
      updates.push(`updated_at = NOW()`);
      await query(
        `UPDATE orders SET ${updates.join(', ')} WHERE id = $${paramIndex}`,
        [...params, id]
      );
    }

    // Update fulfillment step
    if (body.fulfillment_step) {
      const { step_name, status: stepStatus, notes } = body.fulfillment_step;
      const validStepNames = ['payment_confirmed', 'document_generation', 'ein_filing', 'notary_scheduling', 'welcome_email', 'final_delivery'];
      const validStepStatuses = ['pending', 'in_progress', 'completed', 'failed', 'skipped'];

      if (!validStepNames.includes(step_name)) {
        return new Response(JSON.stringify({ error: `Invalid step_name. Must be one of: ${validStepNames.join(', ')}` }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (!validStepStatuses.includes(stepStatus)) {
        return new Response(JSON.stringify({ error: `Invalid step status. Must be one of: ${validStepStatuses.join(', ')}` }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        });
      }

      const completedAt = stepStatus === 'completed' ? ', completed_at = NOW()' : '';

      await query(
        `UPDATE fulfillment_steps 
         SET status = $1${completedAt}, notes = COALESCE($2, notes)
         WHERE order_id = $3 AND step_name = $4`,
        [stepStatus, notes || null, id, step_name]
      );
    }

    // Return updated order
    const updated = await query(
      `SELECT o.*, c.name as customer_name, c.email as customer_email
       FROM orders o JOIN customers c ON c.id = o.customer_id
       WHERE o.id = $1`,
      [id]
    );

    return new Response(JSON.stringify({ order: updated.rows[0] }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error updating order:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
