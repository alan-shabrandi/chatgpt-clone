This file is a merged representation of a subset of the codebase, containing specifically included files, combined into a single document by Repomix.

# File Summary

## Purpose
This file contains a packed representation of a subset of the repository's contents that is considered the most important context.
It is designed to be easily consumable by AI systems for analysis, code review,
or other automated processes.

## File Format
The content is organized as follows:
1. This summary section
2. Repository information
3. Directory structure
4. Repository files (if enabled)
5. Multiple file entries, each consisting of:
  a. A header with the file path (## File: path/to/file)
  b. The full contents of the file in a code block

## Usage Guidelines
- This file should be treated as read-only. Any changes should be made to the
  original repository files, not this packed version.
- When processing this file, use the file path to distinguish
  between different files in the repository.
- Be aware that this file may contain sensitive information. Handle it with
  the same level of security as you would the original repository.

## Notes
- Some files may have been excluded based on .gitignore rules and Repomix's configuration
- Binary files are not included in this packed representation. Please refer to the Repository Structure section for a complete list of file paths, including binary files
- Only files matching these patterns are included: ./frontend/components/chat/ChatArea.tsx, ./frontend/components/layout/Sidebar.tsx, ./frontend/app/page.tsx
- Files matching patterns in .gitignore are excluded
- Files matching default ignore patterns are excluded
- Files are sorted by Git change count (files with more changes are at the bottom)

# Directory Structure
```
./frontend/app/page.tsx
./frontend/components/chat/ChatArea.tsx
./frontend/components/layout/Sidebar.tsx
```

# Files

## File: ./frontend/app/page.tsx
```typescript
"use client";

import ChatArea from "@/components/chat/ChatArea";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";

export default function Home() {
  return (
    <main className="h-screen bg-background text-foreground">
      <div className="flex h-full">
        <Sidebar />

        <section className="flex min-w-0 flex-1 flex-col">
          <Header />

          <ChatArea />
        </section>
      </div>
    </main>
  );
}
```

## File: ./frontend/components/chat/ChatArea.tsx
```typescript
"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";

import ChatInput from "./ChatInput";
import ChatMessage from "./ChatMessage";
import EmptyState from "./EmptyState";
import TypingIndicator from "./TypingIndicator";
import { Message } from "./types";

export default function ChatArea() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;

    const isUserLogged = localStorage.getItem("user_logged_in") === "true";
    if (!isUserLogged) {
      router.push("/login");
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: text,
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_BACKEND_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            message: text,
          }),
        },
      );

      if (response.status === 401) {
        localStorage.removeItem("user_logged_in");
        router.push("/login");
        router.refresh();
        throw new Error("Session expired. Please log in again.");
      }

      if (!response.ok) {
        throw new Error("Request failed");
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error("No response stream");
      }

      const decoder = new TextDecoder();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "",
        },
      ]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, {
          stream: true,
        });

        setMessages((prev) => {
          const copy = [...prev];
          copy[copy.length - 1] = {
            ...copy[copy.length - 1],
            content: copy[copy.length - 1].content + chunk,
          };
          return copy;
        });
      }
    } catch (error: any) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: error.message || "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-64px)] flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto flex max-w-4xl flex-col gap-6 px-6 py-8 pb-40">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage key={index} message={message} />
              ))}

              {loading && <TypingIndicator />}
            </>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <ChatInput loading={loading} onSend={handleSend} />
    </div>
  );
}
```

## File: ./frontend/components/layout/Sidebar.tsx
```typescript
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
```
