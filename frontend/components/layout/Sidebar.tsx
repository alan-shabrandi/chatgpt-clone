"use client";

import { MessageSquare, Plus, Settings } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

const todayChats = ["Explain React Hooks", "Python API"];

const yesterdayChats = ["AI Image Generation"];

export default function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 border-r bg-background md:flex md:flex-col">
      {/* Header */}

      <div className="p-4">
        <Button className="w-full justify-start gap-2">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <Separator />

      {/* Chat History */}

      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-6">
          <div>
            <p className="mb-2 px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Today
            </p>

            <div className="space-y-1">
              {todayChats.map((chat, index) => (
                <Button
                  key={chat}
                  variant={index === 0 ? "secondary" : "ghost"}
                  className="w-full justify-start gap-2 truncate"
                >
                  <MessageSquare className="h-4 w-4 shrink-0" />

                  <span className="truncate">{chat}</span>
                </Button>
              ))}
            </div>
          </div>

          <div>
            <p className="mb-2 px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Yesterday
            </p>

            <div className="space-y-1">
              {yesterdayChats.map((chat) => (
                <Button
                  key={chat}
                  variant="ghost"
                  className="w-full justify-start gap-2 truncate"
                >
                  <MessageSquare className="h-4 w-4 shrink-0" />

                  <span className="truncate">{chat}</span>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </ScrollArea>

      <Separator />

      {/* Footer */}

      <div className="p-3">
        <Button variant="ghost" className="w-full justify-start gap-2">
          <Settings className="h-4 w-4" />
          Settings
        </Button>
      </div>
    </aside>
  );
}
