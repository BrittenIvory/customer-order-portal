"use client";

import Link from "next/link";
import type { OrderSummary } from "@/types";
import StatusTracker from "./StatusTracker";

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Date(dateStr).toLocaleDateString("en-AU", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatCurrency(amount: number | null): string {
  if (amount == null) return "—";
  return new Intl.NumberFormat("en-AU", {
    style: "currency",
    currency: "AUD",
  }).format(amount);
}

export default function OrderCard({ order }: { order: OrderSummary }) {
  return (
    <Link href={`/orders/${encodeURIComponent(order.order_nbr)}`}>
      <div className="bg-card rounded-xl border border-border p-6 hover:shadow-lg hover:border-primary-light/30 transition-all cursor-pointer">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-foreground">
              Order #{order.order_nbr}
            </h3>
            <p className="text-sm text-muted mt-0.5">
              {formatDate(order.order_date)} &middot; {order.line_count} item
              {order.line_count !== 1 ? "s" : ""}
            </p>
          </div>
          <div className="text-right">
            <span className="text-lg font-semibold text-foreground">
              {formatCurrency(order.total_amount)}
            </span>
          </div>
        </div>

        {order.description && (
          <p className="text-sm text-muted mb-4 truncate">{order.description}</p>
        )}

        <div className="mb-3">
          <StatusTracker currentStatus={order.overall_status} compact />
        </div>

        <div className="flex items-center justify-between">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-primary-light/10 text-primary">
            {order.overall_status}
          </span>
          <span className="text-xs text-muted">View details →</span>
        </div>
      </div>
    </Link>
  );
}
