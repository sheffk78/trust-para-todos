import type { APIRoute } from 'astro';
import { query } from '../../../lib/db';

/**
 * POST /api/orders/create-direct
 *
 * Public endpoint called by the evaluation form (/evaluacion).
 * Creates a customer + order + fulfillment steps + questionnaire response
 * from the form data, then redirects to the customer panel.
 *
 * This is NOT a payment endpoint — the order is created in 'pending' status.
 */
export const POST: APIRoute = async (context) => {
  try {
    const body = await context.request.json();

    // Validate required fields
    const required = ['settlor_1_full_name', 'email'];
    for (const field of required) {
      if (!body[field] || !String(body[field]).trim()) {
        return new Response(JSON.stringify({
          error: `Campo requerido: ${field}`,
        }), {
          status: 400,
          headers: { 'Content-Type': 'application/json' },
        });
      }
    }

    // Check if customer already exists by email
    const existingCustomer = await query(
      'SELECT id FROM customers WHERE email = $1',
      [body.email.trim().toLowerCase()]
    );

    let customerId: string;

    if (existingCustomer.rows.length > 0) {
      // Update existing customer
      customerId = existingCustomer.rows[0].id;
      await query(
        `UPDATE customers SET name = $1, phone = $2, visa_type = $3, updated_at = NOW()
         WHERE id = $4`,
        [
          body.settlor_1_full_name.trim(),
          body.phone?.trim() || null,
          body.citizenship || null,
          customerId,
        ]
      );
    } else {
      // Create new customer
      const customerResult = await query(
        `INSERT INTO customers (name, email, phone, visa_type)
         VALUES ($1, $2, $3, $4)
         RETURNING id`,
        [
          body.settlor_1_full_name.trim(),
          body.email.trim().toLowerCase(),
          body.phone?.trim() || null,
          body.citizenship || null,
        ]
      );
      customerId = customerResult.rows[0].id;
    }

    // Determine plan and amount
    const planType = body.plan_type === 'complete' ? 'complete' : 'base';
    const amount = planType === 'base' ? 99700 : 149700; // cents

    // Create order
    const orderResult = await query(
      `INSERT INTO orders (customer_id, plan_type, amount, status)
       VALUES ($1, $2, $3, 'pending')
       RETURNING id`,
      [customerId, planType, amount]
    );
    const orderId = orderResult.rows[0].id;

    // Store questionnaire response
    await query(
      `INSERT INTO questionnaire_responses (customer_id, raw_data)
       VALUES ($1, $2)`,
      [customerId, JSON.stringify(body)]
    );

    // Create fulfillment steps — insurance_verification first, then the standard flow
    const steps = [
      { name: 'insurance_verification', status: 'pending' },
      { name: 'payment_confirmed', status: 'pending' },
      { name: 'document_generation', status: 'pending' },
      { name: 'ein_filing', status: 'pending' },
      { name: 'notary_scheduling', status: 'pending' },
      { name: 'welcome_email', status: 'pending' },
      { name: 'final_delivery', status: 'pending' },
    ];

    // If user already has insurance, mark verification as completed
    if (body.has_insurance === 'yes') {
      steps[0].status = 'completed';
    } else if (body.has_insurance === 'no' && body.insurance_consulted) {
      steps[0].status = 'completed';
    }

    for (const step of steps) {
      await query(
        `INSERT INTO fulfillment_steps (order_id, step_name, status, completed_at)
         VALUES ($1, $2, $3, $4)`,
        [
          orderId,
          step.name,
          step.status,
          step.status === 'completed' ? new Date().toISOString() : null,
        ]
      );
    }

    // Return panel URL
    const panelUrl = `/panel?order_id=${orderId}&email=${encodeURIComponent(body.email.trim())}&status=created`;

    return new Response(JSON.stringify({
      order_id: orderId,
      panel_url: panelUrl,
      message: 'Orden creada exitosamente',
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (e) {
    console.error('Error creating order:', e);
    return new Response(JSON.stringify({
      error: 'Error al crear la orden. Intenta de nuevo.',
      detail: String(e),
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};