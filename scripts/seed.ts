/**
 * Trust Para Todos — Database Seed Script
 *
 * Inserts sample customers, orders, fulfillment steps, and documents
 * so the admin dashboard and customer panel have data to display.
 *
 * Usage: npx tsx scripts/seed.ts
 * Requires DATABASE_URL env var to be set.
 */
import pg from 'pg';

const { Pool } = pg;

const CUSTOMERS = [
  { name: 'María García', email: 'maria@example.com', phone: '+52 55 1234 5678' },
  { name: 'Carlos Rodríguez', email: 'carlos@example.com', phone: '+52 81 2345 6789' },
  { name: 'Ana Martínez', email: 'ana@example.com', phone: '+52 33 3456 7890' },
  { name: 'José Hernández', email: 'jose@example.com', phone: '+52 55 4567 8901' },
  { name: 'Luisa Fernández', email: 'luisa@example.com', phone: '+52 81 5678 9012' },
  { name: 'Roberto López', email: 'roberto@example.com', phone: '+52 33 6789 0123' },
  { name: 'Sofía Torres', email: 'sofia@example.com', phone: '+52 55 7890 1234' },
  { name: 'Diego Ramírez', email: 'diego@example.com', phone: '+52 81 8901 2345' },
  { name: 'Valentina Ortiz', email: 'valentina@example.com', phone: '+52 33 9012 3456' },
  { name: 'Fernando Castillo', email: 'fernando@example.com', phone: '+52 55 0123 4567' },
];

const PLAN_TYPES = ['base', 'completo'] as const;
const STATUSES = ['pending', 'paid', 'fulfilling', 'complete'] as const;

const STEP_NAMES = [
  'payment_confirmed',
  'document_generation',
  'ein_filing',
  'notary_scheduling',
  'welcome_email',
  'final_delivery',
] as const;

const DOC_TYPES_BASE = [
  'trust',
  'guide',
] as const;

const DOC_TYPES_COMPLETO = [
  ...DOC_TYPES_BASE,
  'ilit',
] as const;

function uuid() {
  return crypto.randomUUID();
}

function daysAgo(n: number): Date {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d;
}

async function main() {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });
  const client = await pool.connect();

  try {
    // Check if data already exists
    const existing = await client.query('SELECT COUNT(*)::int as count FROM customers');
    if (existing.rows[0].count > 0) {
      console.log(`Database already has ${existing.rows[0].count} customers — skipping seed.`);
      return;
    }

    console.log('Seeding database with sample data...');

    for (let i = 0; i < CUSTOMERS.length; i++) {
      const c = CUSTOMERS[i];
      const customerId = uuid();
      const daysBack = 30 - i * 2; // spread orders over the last ~30 days
      const createdAt = daysAgo(daysBack);

      // Insert customer
      await client.query(
        `INSERT INTO customers (id, name, email, phone, created_at)
         VALUES ($1, $2, $3, $4, $5)`,
        [customerId, c.name, c.email, c.phone, createdAt]
      );

      // 1-2 orders per customer
      const numOrders = i % 3 === 0 ? 2 : 1;
      for (let o = 0; o < numOrders; o++) {
        const orderId = uuid();
        const planType = i % 2 === 0 ? 'base' : 'completo';
        const amount = planType === 'base' ? 99700 : 149400;
        const statusIdx = Math.min(i + o, STATUSES.length - 1);
        const status = STATUSES[statusIdx];
        const orderCreated = daysAgo(daysBack - o * 3);
        const orderUpdated = status === 'complete' ? daysAgo(daysBack - 5) : new Date();

        await client.query(
          `INSERT INTO orders (id, customer_id, plan_type, amount, status, created_at, updated_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7)`,
          [orderId, customerId, planType, amount, status, orderCreated, orderUpdated]
        );

        // Fulfillment steps
        const stepStatuses = getStepStatuses(status);
        for (let s = 0; s < STEP_NAMES.length; s++) {
          const stepId = uuid();
          const stepStatus = stepStatuses[s];
          const completedAt = stepStatus === 'completed' ? daysAgo(daysBack - 5 + s) : null;

          await client.query(
            `INSERT INTO fulfillment_steps (id, order_id, step_name, status, completed_at, created_at)
             VALUES ($1, $2, $3, $4, $5, $6)`,
            [stepId, orderId, STEP_NAMES[s], stepStatus, completedAt, orderCreated]
          );
        }

        // Documents
        const docTypes = planType === 'completo' ? DOC_TYPES_COMPLETO : DOC_TYPES_BASE;
        for (let d = 0; d < docTypes.length; d++) {
          const docId = uuid();
          const docStatus = status === 'complete' || status === 'fulfilling' ? 'ready' : 'pending';
          const filePath = docStatus === 'ready' ? `/docs/${orderId}/${docTypes[d]}.pdf` : null;

          await client.query(
            `INSERT INTO documents (id, order_id, document_type, status, file_path, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6, $7)`,
            [docId, orderId, docTypes[d], docStatus, filePath, orderCreated, orderCreated]
          );
        }
      }
    }

    console.log('✅ Seed complete!');
    console.log(`   ${CUSTOMERS.length} customers`);
    console.log(`   ${(await client.query('SELECT COUNT(*)::int as c FROM orders')).rows[0].c} orders`);
    console.log(`   ${(await client.query('SELECT COUNT(*)::int as c FROM fulfillment_steps')).rows[0].c} fulfillment steps`);
    console.log(`   ${(await client.query('SELECT COUNT(*)::int as c FROM documents')).rows[0].c} documents`);

  } finally {
    client.release();
    await pool.end();
  }
}

function getStepStatuses(orderStatus: string): string[] {
  const statusOrder = ['pending', 'paid', 'fulfilling', 'complete'];
  const idx = statusOrder.indexOf(orderStatus);

  return STEP_NAMES.map((_, i) => {
    if (i < idx) return 'completed';
    if (i === idx) return 'completed'; // current step is also completed
    if (i === idx + 1 && orderStatus === 'fulfilling') return 'in_progress';
    return 'pending';
  });
}

main().catch((e) => {
  console.error('Seed failed:', e);
  process.exit(1);
});
