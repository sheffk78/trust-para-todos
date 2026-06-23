/**
 * Trust Para Todos — Database connection (pg)
 *
 * Connects to Postgres via DATABASE_URL env var.
 * Exports a singleton pool and helpers for running queries.
 */
import pg from 'pg';
import type {
  CustomerRow,
  CustomerWithOrderCount,
  OrderListItem,
  OrderWithCustomer,
  FulfillmentStepRow,
  DocumentRow,
  QuestionnaireResponseRow,
  DashboardStatsResponse,
} from './types';

const { Pool } = pg;

let pool: pg.Pool | null = null;

function getPool(): pg.Pool {
  if (!pool) {
    const connectionString = import.meta.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error('DATABASE_URL environment variable is not set');
    }
    pool = new Pool({ connectionString });
  }
  return pool;
}

export async function query(text: string, params?: unknown[]): Promise<pg.QueryResult> {
  const client = await getPool().connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
}

export async function queryOne(text: string, params?: unknown[]): Promise<pg.QueryResultRow | null> {
  const result = await query(text, params);
  return result.rows[0] || null;
}

export async function endPool(): Promise<void> {
  if (pool) {
    await pool.end();
    pool = null;
  }
}

/**
 * Escape HTML to prevent XSS in innerHTML rendering.
 */
export function escapeHtml(str: string | number | null | undefined): string {
  if (str == null) return '';
  const s = String(str);
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/**
 * Safely parse a page number from query params.
 */
export function safePage(page: string | null, defaultVal: number = 1): number {
  const n = parseInt(page || '', 10);
  return Number.isFinite(n) && n >= 1 ? n : defaultVal;
}

/**
 * Safely parse a limit number from query params.
 */
export function safeLimit(limit: string | null, defaultVal: number = 50, maxVal: number = 200): number {
  const n = parseInt(limit || '', 10);
  return Number.isFinite(n) && n >= 1 ? Math.min(n, maxVal) : defaultVal;
}

// ── Typed query helpers ────────────────────────────

export async function getDashboardStats(): Promise<DashboardStatsResponse> {
  const totalOrders = await queryOne('SELECT COUNT(*)::int as count FROM orders');
  const ordersToday = await queryOne(
    "SELECT COUNT(*)::int as count FROM orders WHERE created_at >= CURRENT_DATE"
  );
  const pendingFulfillment = await queryOne(
    "SELECT COUNT(*)::int as count FROM orders WHERE status IN ('paid', 'fulfilling')"
  );
  const revenue = await queryOne(
    "SELECT COALESCE(SUM(amount), 0)::float / 100 as total FROM orders WHERE status IN ('paid', 'fulfilling', 'complete')"
  );
  const recentOrders = await query(
    `SELECT o.id, o.plan_type, o.status, o.amount, o.created_at, o.updated_at,
            c.id as customer_id, c.name as customer_name, c.email as customer_email
     FROM orders o
     JOIN customers c ON c.id = o.customer_id
     ORDER BY o.created_at DESC
     LIMIT 10`
  );

  return {
    total_orders: totalOrders?.count || 0,
    orders_today: ordersToday?.count || 0,
    pending_fulfillment: pendingFulfillment?.count || 0,
    revenue: revenue?.total || 0,
    recent_orders: recentOrders.rows as OrderListItem[],
  };
}

export async function getOrdersList(params: {
  search?: string;
  status?: string;
  plan?: string;
  limit: number;
  offset: number;
}): Promise<{ orders: OrderListItem[]; total: number }> {
  const { search, status, plan, limit, offset } = params;
  const whereClauses: string[] = [];
  const queryParams: unknown[] = [];
  let paramIndex = 1;

  if (search) {
    whereClauses.push(`(c.name ILIKE $${paramIndex} OR c.email ILIKE $${paramIndex})`);
    queryParams.push(`%${search}%`);
    paramIndex++;
  }
  if (status) {
    whereClauses.push(`o.status = $${paramIndex}`);
    queryParams.push(status);
    paramIndex++;
  }
  if (plan) {
    whereClauses.push(`o.plan_type = $${paramIndex}`);
    queryParams.push(plan);
    paramIndex++;
  }

  const whereSQL = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

  const countResult = await query(
    `SELECT COUNT(*)::int as total FROM orders o JOIN customers c ON c.id = o.customer_id ${whereSQL}`,
    queryParams
  );
  const total = countResult.rows[0]?.total || 0;

  const result = await query(
    `SELECT o.id, o.plan_type, o.status, o.amount, o.created_at, o.updated_at,
            c.id as customer_id, c.name as customer_name, c.email as customer_email
     FROM orders o
     JOIN customers c ON c.id = o.customer_id
     ${whereSQL}
     ORDER BY o.created_at DESC
     LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`,
    [...queryParams, limit, offset]
  );

  return { orders: result.rows as OrderListItem[], total };
}

export async function getOrderDetail(id: string): Promise<{
  order: OrderWithCustomer | null;
  fulfillment_steps: FulfillmentStepRow[];
  documents: DocumentRow[];
}> {
  const orderResult = await query(
    `SELECT o.*, c.name as customer_name, c.email as customer_email, c.phone as customer_phone
     FROM orders o
     JOIN customers c ON c.id = o.customer_id
     WHERE o.id = $1`,
    [id]
  );

  if (orderResult.rows.length === 0) {
    return { order: null, fulfillment_steps: [], documents: [] };
  }

  const stepsResult = await query(
    `SELECT * FROM fulfillment_steps WHERE order_id = $1 ORDER BY created_at ASC`,
    [id]
  );

  const docsResult = await query(
    `SELECT * FROM documents WHERE order_id = $1 ORDER BY created_at ASC`,
    [id]
  );

  return {
    order: orderResult.rows[0] as OrderWithCustomer,
    fulfillment_steps: stepsResult.rows as FulfillmentStepRow[],
    documents: docsResult.rows as DocumentRow[],
  };
}

export async function getCustomersList(params: {
  search?: string;
  limit: number;
  offset: number;
}): Promise<{ customers: CustomerWithOrderCount[]; total: number }> {
  const { search, limit, offset } = params;
  const whereClauses: string[] = [];
  const queryParams: unknown[] = [];
  let paramIndex = 1;

  if (search) {
    whereClauses.push(`(c.name ILIKE $${paramIndex} OR c.email ILIKE $${paramIndex})`);
    queryParams.push(`%${search}%`);
    paramIndex++;
  }

  const whereSQL = whereClauses.length > 0 ? `WHERE ${whereClauses.join(' AND ')}` : '';

  const countResult = await query(
    `SELECT COUNT(*)::int as total FROM customers c ${whereSQL}`,
    queryParams
  );
  const total = countResult.rows[0]?.total || 0;

  const result = await query(
    `SELECT c.*, COUNT(o.id)::int as order_count
     FROM customers c
     LEFT JOIN orders o ON o.customer_id = c.id
     ${whereSQL}
     GROUP BY c.id
     ORDER BY c.created_at DESC
     LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`,
    [...queryParams, limit, offset]
  );

  return { customers: result.rows as CustomerWithOrderCount[], total };
}

export async function getCustomerDetail(id: string): Promise<{
  customer: CustomerRow | null;
  orders: (import('./types').OrderRow & { document_count: number })[];
  questionnaire_responses: QuestionnaireResponseRow[];
}> {
  const customerResult = await query('SELECT * FROM customers WHERE id = $1', [id]);
  if (customerResult.rows.length === 0) {
    return { customer: null, orders: [], questionnaire_responses: [] };
  }

  const ordersResult = await query(
    `SELECT o.*, 
      (SELECT COUNT(*)::int FROM documents WHERE order_id = o.id) as document_count
     FROM orders o 
     WHERE o.customer_id = $1 
     ORDER BY o.created_at DESC`,
    [id]
  );

  const qResult = await query(
    'SELECT * FROM questionnaire_responses WHERE customer_id = $1 ORDER BY created_at DESC',
    [id]
  );

  return {
    customer: customerResult.rows[0] as CustomerRow,
    orders: ordersResult.rows as (import('./types').OrderRow & { document_count: number })[],
    questionnaire_responses: qResult.rows as QuestionnaireResponseRow[],
  };
}
