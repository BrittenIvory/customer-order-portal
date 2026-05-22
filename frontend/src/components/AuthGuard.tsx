"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import Navbar from "./Navbar";

export default function AuthGuard({
  children,
  requireAdmin = false,
}: {
  children: React.ReactNode;
  requireAdmin?: boolean;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/");
    }
    if (!loading && user && requireAdmin && !user.is_admin) {
      router.replace("/dashboard");
    }
  }, [user, loading, router, requireAdmin]);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-4 border-primary-light border-t-transparent rounded-full" />
      </div>
    );
  }

  if (!user) return null;
  if (requireAdmin && !user.is_admin) return null;

  return (
    <>
      <Navbar />
      <main className="flex-1">{children}</main>
    </>
  );
}
