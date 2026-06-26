"use client";

import { signIn } from "next-auth/react";
import { Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function LoginPage() {
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
          {/* Google Login */}
          <Button
            variant="outline"
            className="w-full"
            onClick={() => signIn("google", { callbackUrl: "/" })}
          >
            Continue with Google
          </Button>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="h-px flex-1 bg-border" />
            <span className="text-xs text-muted-foreground">OR</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          {/* Email Login */}
          <form
            className="space-y-4"
            onSubmit={(e) => {
              e.preventDefault();
              const form = e.currentTarget;
              const email = (form.email as HTMLInputElement).value;
              const password = (form.password as HTMLInputElement).value;

              signIn("credentials", {
                email,
                password,
                callbackUrl: "/",
              });
            }}
          >
            <div className="space-y-2">
              <Label>Email</Label>
              <Input name="email" type="email" placeholder="you@example.com" />
            </div>

            <div className="space-y-2">
              <Label>Password</Label>
              <Input name="password" type="password" placeholder="••••••••" />
            </div>

            <Button className="w-full">Sign in</Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
