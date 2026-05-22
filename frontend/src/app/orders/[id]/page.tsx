"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import AuthGuard from "@/components/AuthGuard";
import StatusTracker from "@/components/StatusTracker";
import { api } from "@/lib/api";
import type { OrderDetail } from "@/types";

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

export default function OrderDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [order, setOrder] = useState<OrderDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .getOrder(id)
      .then(setOrder)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  return (
    <AuthGuard>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Link
          href="/dashboard"
          className="inline-flex items-center text-sm text-muted hover:text-foreground mb-6 transition-colors"
        >
          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Orders
        </Link>

        {loading && (
          <div className="flex justify-center py-20">
            <div className="animate-spin w-8 h-8 border-4 border-primary-light border-t-transparent rounded-full" />
          </div>
        )}

        {error && (
          <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700">
            {error}
          </div>
        )}

        {order && (
          <>
            <div className="bg-card rounded-xl border border-border p-6 mb-6">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between mb-6">
                <div>
                  <h1 className="text-2xl font-bold text-foreground">
                    Order #{order.order_nbr}
                  </h1>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-sm text-muted">
                    <span>Ordered: {formatDate(order.order_date)}</span>
                    {order.customer_order_ref && (
                      <span>Your Ref: {order.customer_order_ref}</span>
                    )}
                    <span>{order.lines.length} line item{order.lines.length !== 1 ? "s" : ""}</span>
                  </div>
                </div>
                <div className="text-right mt-4 sm:mt-0">
                  <div className="text-2xl font-bold text-foreground">
                    {formatCurrency(order.total_amount)}
                  </div>
                </div>
              </div>

              <StatusTracker currentStatus={order.overall_status} />
            </div>

            <h2 className="text-lg font-semibold text-foreground mb-4">
              Line Items
            </h2>
            <div className="space-y-3">
              {order.lines.map((line) => (
                <div
                  key={line.line_nbr}
                  className="bg-card rounded-xl border border-border p-5"
                >
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-foreground">
                          {line.inventory_id}
                        </span>
                        <span className="text-xs px-2 py-0.5 rounded-full bg-primary-light/10 text-primary font-medium">
                          {line.status}
                        </span>
                      </div>
                      {line.description && (
                        <p className="text-sm text-muted mt-1">
                          {line.description}
                        </p>
                      )}
                      <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-sm text-muted">
                        <span>Qty: {line.quantity}</span>
                        {line.unit_price != null && (
                          <span>Unit: {formatCurrency(line.unit_price)}</span>
                        )}
                        {line.line_total != null && (
                          <span>Total: {formatCurrency(line.line_total)}</span>
                        )}
                      </div>
                    </div>
                    <div className="sm:text-right text-sm space-y-1">
                      {line.po_order_nbr && (
                        <div className="text-muted">
                          PO: {line.po_order_nbr}
                        </div>
                      )}
                      {line.estimated_delivery && (
                        <div className="text-foreground font-medium">
                          Est. Delivery: {formatDate(line.estimated_delivery)}
                        </div>
                      )}
                      {line.inspected_at && (
                        <div className="text-success">
                          Inspected: {formatDate(line.inspected_at)}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="mt-3">
                    <StatusTracker currentStatus={line.status} compact />
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </AuthGuard>
  );
}
