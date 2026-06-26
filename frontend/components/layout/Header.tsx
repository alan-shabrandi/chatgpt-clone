"use client";

import { Sparkles } from "lucide-react";

import { Button } from "@/components/ui/button";

export default function Header() {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-background/80 px-6 backdrop-blur supports-backdrop-filter:bg-background/60">
      <div className="flex items-center gap-3">
        <Sparkles className="h-5 w-5 text-primary" />

        <div>
          <h1 className="text-sm font-semibold">AI Assistant</h1>

          <p className="text-xs text-muted-foreground">GPT-4 Powered</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Button size="sm">Login</Button>
      </div>
    </header>
  );
}
