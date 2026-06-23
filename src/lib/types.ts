/**
 * Trust Para Todos — Shared TypeScript types for DB rows and API responses.
 */

// ── Enums ──────────────────────────────────────────

export type PlanType = 'base' | 'completo';
export type OrderStatus = 'pending' | 'paid' | 'fulfilling' | 'complete';
export type DocumentType = 'trust' | 'ilit' | 'ein' | 'guide';
export type DocumentStatus = 'pending' | 'generating' | 'ready' | 'error';
export type FulfillmentStepName =
  | 'payment_confirmed'
  | 'document_generation'
  | 'ein_filing'
  | 'notary_scheduling'
  | 'welcome_email'
  | 'final_delivery';
export type FulfillmentStepStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';

// ── DB Row Types ───────────────────────────────────

export interface CustomerRow {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  visa_type: string | null;
  created_at: string;
}

export interface CustomerWithOrderCount extends CustomerRow {
  order_count: number;
}

export interface OrderRow {
  id: string;
  customer_id: string;
  plan_type: PlanType;
  amount: number;
  status: OrderStatus;
  stripe_session_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrderWithCustomer extends OrderRow {
  customer_name: string;
  customer_email: string;
  customer_phone: string | null;
}

export interface OrderListItem {
  id: string;
  plan_type: PlanType;
  status: OrderStatus;
  amount: number;
  created_at: string;
  updated_at: string;
  customer_id: string;
  customer_name: string;
  customer_email: string;
}

export interface FulfillmentStepRow {
  id: string;
  order_id: string;
  step_name: FulfillmentStepName;
  status: FulfillmentStepStatus;
  completed_at: string | null;
  notes: string | null;
  created_at: string;
}

export interface DocumentRow {
  id: string;
  order_id: string;
  document_type: DocumentType;
  status: DocumentStatus;
  file_path: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface QuestionnaireResponseRow {
  id: string;
  customer_id: string;
  raw_data: Record<string, unknown>;
  created_at: string;
}

// ── API Response Types ──────────────────────────────

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  limit: number;
}

export interface OrdersListResponse extends PaginatedResponse<OrderListItem> {
  orders: OrderListItem[];
}

export interface OrderDetailResponse {
  order: OrderWithCustomer;
  fulfillment_steps: FulfillmentStepRow[];
  documents: DocumentRow[];
}

export interface CustomersListResponse extends PaginatedResponse<CustomerWithOrderCount> {
  customers: CustomerWithOrderCount[];
}

export interface CustomerDetailResponse {
  customer: CustomerRow;
  orders: (OrderRow & { document_count: number })[];
  questionnaire_responses: QuestionnaireResponseRow[];
}

export interface DashboardStatsResponse {
  total_orders: number;
  orders_today: number;
  pending_fulfillment: number;
  revenue: number;
  recent_orders: OrderListItem[];
}

export interface ApiError {
  error: string;
}
