import type { APIRoute } from 'astro';
import { query } from '../../../../lib/db';
import { requireAdmin } from '../../../../lib/auth';

// Map each document key to its proper document_type value
const DOC_TYPE_MAP: Record<string, string> = {
  revocable_living_trust: 'trust',
  pour_over_will: 'trust',
  certificate_of_trust: 'trust',
  assignment_of_property: 'trust',
  durable_power_of_attorney: 'trust',
  advance_healthcare_directive: 'trust',
};

// Human-readable labels for the document types
const DOC_LABELS: Record<string, string> = {
  revocable_living_trust: 'Revocable Living Trust',
  pour_over_will: 'Pour-Over Will',
  certificate_of_trust: 'Certificate of Trust',
  assignment_of_property: 'Assignment of Property',
  durable_power_of_attorney: 'Durable Power of Attorney',
  advance_healthcare_directive: 'Advance Healthcare Directive',
};

export const POST: APIRoute = async (context) => {
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

    const order = orderResult.rows[0];

    // Update document generation step to in_progress
    await query(
      `UPDATE fulfillment_steps SET status = 'in_progress' 
       WHERE order_id = $1 AND step_name = 'document_generation'`,
      [id]
    );

    // Update order status to fulfilling
    await query(
      `UPDATE orders SET status = 'fulfilling', updated_at = NOW() WHERE id = $1`,
      [id]
    );

    // Delete existing documents for this order (clean slate on regenerate)
    await query('DELETE FROM documents WHERE order_id = $1', [id]);

    // Determine which docs to generate
    const docTypes = order.plan_type === 'completo' 
      ? ['revocable_living_trust', 'pour_over_will', 'certificate_of_trust', 'assignment_of_property', 'durable_power_of_attorney', 'advance_healthcare_directive']
      : ['revocable_living_trust'];

    const generated: Array<{ id: string; document_type: string; status: string; label: string }> = [];

    // Create document records as "generating"
    for (const dt of docTypes) {
      const docResult = await query(
        `INSERT INTO documents (order_id, document_type, status, created_at, updated_at)
         VALUES ($1, $2, 'generating', NOW(), NOW())
         RETURNING id, document_type, status`,
        [id, DOC_TYPE_MAP[dt] || 'trust']
      );
      generated.push({
        ...docResult.rows[0],
        label: DOC_LABELS[dt] || dt,
      });
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Document generation triggered',
      documents: generated,
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error generating docs:', e);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
