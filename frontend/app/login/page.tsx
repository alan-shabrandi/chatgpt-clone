"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Sparkles, Loader2 } from "lucide-react";
import { signIn } from "next-auth/react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showSuccess, setShowSuccess] = useState(false);

  // بررسی اینکه آیا کاربر از صفحه ثبت‌نام ریدایرکت شده است یا خیر
  useEffect(() => {
    if (searchParams.get("registered") === "true") {
      setShowSuccess(true);
    }
  }, [searchParams]);

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    try {
      // ورود با گوگل از طریق NextAuth
      await signIn("google", { callbackUrl: "/" });
    } catch (err) {
      setError("Google authentication failed.");
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setShowSuccess(false);

    const form = e.currentTarget;
    const username = (form.elements.namedItem("username") as HTMLInputElement)
      .value;
    const password = (form.elements.namedItem("password") as HTMLInputElement)
      .value;

    try {
      // تبدیل داده‌ها به فرمت x-www-form-urlencoded برای مطابقت با OAuth2 در FastAPI
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        // 👈 بسیار مهم: اجازه دریافت و ثبت کوکی HttpOnly را صادر می‌کند
        credentials: "include",
        body: formData.toString(),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Invalid username or password");
      }

      // 👈 تنظیم فلگ ظاهری برای بروزرسانی UI کامپوننت‌های فرانت‌اند (مثل هدر)
      localStorage.setItem("user_logged_in", "true");

      // هدایت کاربر به داشبورد یا صفحه اصلی چت و تازه سازی مسیرها
      router.push("/");
      router.refresh();
    } catch (err: any) {
      setError(err.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background px-4">
      <Card className="w-full max-w-md">
        {/* Header */}
        <CardHeader className="text-center space-y-3">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
            <Sparkles className="h-6 w-6 text-primary" />
          </div>

          <div>
            <h1 className="text-2xl font-semibold">Welcome back</h1>
            <p className="text-sm text-muted-foreground mt-2">
              Sign in to continue to AI Assistant
            </p>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* پیام موفقیت‌آمیز بودن ثبت نام */}
          {showSuccess && (
            <div className="p-3 text-sm text-green-600 bg-green-50 dark:bg-green-950/30 dark:text-green-400 rounded-md text-center font-medium">
              Account created successfully! Please sign in.
            </div>
          )}

          {/* نمایش خطاها */}
          {error && (
            <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md text-center font-medium">
              {error}
            </div>
          )}

          {/* Google Login */}
          <Button
            variant="outline"
            className="w-full"
            onClick={handleGoogleLogin}
            disabled={isLoading}
          >
            Continue with Google
          </Button>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs text-muted-foreground">OR</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          {/* Username/Email Login Form */}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="space-y-2">
              <Label htmlFor="username">Username / Email</Label>
              <Input
                id="username"
                name="username"
                type="text"
                placeholder="johndoe@example.com"
                required
                disabled={isLoading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                required
                disabled={isLoading}
              />
            </div>

            <Button className="w-full" type="submit" disabled={isLoading}>
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                "Sign in"
              )}
            </Button>
          </form>

          {/* Link to Register */}
          <p className="text-center text-sm text-muted-foreground">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-primary hover:underline">
              Sign up
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
