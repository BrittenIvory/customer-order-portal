export type OrderStatus =
  | "Waiting for Production"
  | "In Production"
  | "In Transit to Warehouse"
  | "In Our Warehouse"
  | "Inspected & Ready to Ship"
  | "Shipped to Customer";

export const STATUS_ORDER: OrderStatus[] = [
  "Waiting for Production",
  "In Production",
  "In Transit to Warehouse",
  "In Our Warehouse",
  "Inspected & Ready to Ship",
  "Shipped to Customer",
];

export interface OrderLineItem {
  line_nbr: number;
  inventory_id: string;
  description: string | null;
  quantity: number;
  unit_price: number | null;
  line_total: number | null;
  status: OrderStatus;
  estimated_delivery: string | null;
  po_order_nbr: string | null;
  po_requested_date: string | null;
  received_date: string | null;
  inspected_at: string | null;
  invoiced_at: string | null;
}

export interface OrderSummary {
  order_nbr: string;
  order_date: string | null;
  customer_id: string;
  customer_name: string | null;
  description: string | null;
  overall_status: OrderStatus;
  total_amount: number | null;
  line_count: number;
  estimated_delivery: string | null;
}

export interface OrderDetail {
  order_nbr: string;
  order_date: string | null;
  customer_id: string;
  customer_name: string | null;
  customer_order_ref: string | null;
  description: string | null;
  overall_status: OrderStatus;
  total_amount: number | null;
  estimated_delivery: string | null;
  lines: OrderLineItem[];
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  company_name: string | null;
  myob_customer_id: string | null;
  is_active: boolean;
  is_admin: boolean;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  company_name?: string;
  myob_customer_id?: string;
  is_admin?: boolean;
}
