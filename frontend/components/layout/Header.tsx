"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Sparkles, LogOut, LogIn, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Header() {
  const router = useRouter();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [checkingAuth, setCheckingAuth] = useState<boolean>(true);

  // بررسی وضعیت لاگین بودن کاربر از طریق یک چک‌آپ ساده با بک‌اند
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        // برای اینکه بفهمیم کوکی معتبر داریم یا نه، یک درخواست تست به بک‌اند می‌زنیم
        // اگر بک‌اند وضعیت را تایید کرد یعنی لاگین هستیم. (می‌توانید یک اندپوینت ساده /auth/me هم بسازید)
        const response = await fetch("http://localhost:8000/auth/google", {
          method: "OPTIONS", // یا هر متد بررسی دیگری، یا گرفتن یک استاتوس کد
          credentials: "include",
        });

        // راه ساده‌تر: چون ما از credentials: "include" استفاده می‌کنیم، کنترل لاگین را
        // می‌توان بر اساس پاسخ اولین درخواست‌ها یا یک استیت سراسری مدیریت کرد.
        // اینجا فرض می‌کنیم کاربر اگر دفعه قبل لاگین کرده، توکن در کوکی جریان دارد.
        // برای سادگی، یک فلگ در localStorage فقط برای ظاهر UI نگه می‌داریم:
        const userLoggedFlag = localStorage.getItem("user_logged_in");
        setIsLoggedIn(userLoggedFlag === "true");
      } catch (err) {
        setIsLoggedIn(false);
      } finally {
        setCheckingAuth(false);
      }
    };

    checkAuthStatus();
  }, []);

  // هندل کردن خروج کاربر و پاک کردن کوکی از سمت FastAPI
  const handleSignOut = async () => {
    try {
      const response = await fetch("http://localhost:8000/logout", {
        method: "POST",
        credentials: "include", // 👈 خیلی مهم: برای اینکه مرورگر اجازه دهد کوکی حذف شود
      });

      if (response.ok) {
        localStorage.removeItem("user_logged_in"); // پاک کردن فلگ ظاهری
        setIsLoggedIn(false);
        router.push("/login");
        router.refresh(); // رفرش کردن مسیرها برای اعمال میدلورها
      }
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-background/80 px-6 backdrop-blur supports-backdrop-filter:bg-background/60">
      {/* سمت چپ: لوگو و عنوان */}
      <div className="flex items-center gap-3">
        <Sparkles className="h-5 w-5 text-primary" />
        <div>
          <h1 className="text-sm font-semibold">AI Assistant</h1>
          <p className="text-xs text-muted-foreground">Qwen-2.5 Powered</p>
        </div>
      </div>

      {/* سمت راست: دکمه وضعیت احراز هویت */}
      <div className="flex items-center gap-3">
        {checkingAuth ? (
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        ) : isLoggedIn ? (
          <Button
            variant="ghost"
            size="sm"
            className="text-muted-foreground hover:text-destructive gap-2"
            onClick={handleSignOut}
          >
            <LogOut className="h-4 w-4" />
            Sign Out
          </Button>
        ) : (
          <Button asChild size="sm" className="gap-2">
            <Link href="/login">
              <LogIn className="h-4 w-4" />
              Login
            </Link>
          </Button>
        )}
      </div>
    </header>
  );
}
