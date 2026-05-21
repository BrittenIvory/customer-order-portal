"use client";

import type { OrderStatus } from "@/types";
import { STATUS_ORDER } from "@/types";

const STATUS_ICONS: Record<OrderStatus, string> = {
  "Waiting for Production": "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z",
  "In Production": "M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z",
  "In Transit to Warehouse": "M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0",
  "In Our Warehouse": "M8 14v3m4-3v3m4-3v3M3 21h18M3 10h18M3 7l9-4 9 4M4 10h16v11H4V10z",
  "Inspected & Ready to Ship": "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z",
  "Shipped to Customer": "M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4",
};

interface StatusTrackerProps {
  currentStatus: OrderStatus;
  compact?: boolean;
}

export default function StatusTracker({
  currentStatus,
  compact = false,
}: StatusTrackerProps) {
  const currentIndex = STATUS_ORDER.indexOf(currentStatus);

  if (compact) {
    return (
      <div className="flex items-center gap-1.5">
        {STATUS_ORDER.map((status, i) => (
          <div
            key={status}
            className={`w-2.5 h-2.5 rounded-full transition-colors ${
              i <= currentIndex ? "bg-primary-light" : "bg-border"
            }`}
            title={status}
          />
        ))}
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between relative">
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-border" />
        <div
          className="absolute top-5 left-0 h-0.5 bg-primary-light transition-all duration-500"
          style={{
            width: `${currentIndex === 0 ? 0 : (currentIndex / (STATUS_ORDER.length - 1)) * 100}%`,
          }}
        />
        {STATUS_ORDER.map((status, i) => {
          const isComplete = i < currentIndex;
          const isCurrent = i === currentIndex;
          const isPending = i > currentIndex;

          return (
            <div
              key={status}
              className="flex flex-col items-center relative z-10"
              style={{ width: `${100 / STATUS_ORDER.length}%` }}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors ${
                  isComplete
                    ? "bg-primary-light border-primary-light text-white"
                    : isCurrent
                      ? "bg-white border-primary-light text-primary-light ring-4 ring-primary-light/20"
                      : "bg-white border-border text-muted"
                }`}
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={isPending ? 1.5 : 2}
                >
                  {isComplete ? (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  ) : (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d={STATUS_ICONS[status]}
                    />
                  )}
                </svg>
              </div>
              <span
                className={`text-xs mt-2 text-center leading-tight ${
                  isCurrent ? "font-semibold text-primary" : isPending ? "text-muted" : "text-foreground"
                }`}
              >
                {status}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
