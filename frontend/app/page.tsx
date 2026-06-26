"use client";

import ChatArea from "@/components/chat/ChatArea";
import Header from "@/components/layout/Header";
import Sidebar from "@/components/layout/Sidebar";

export default function Home() {
  return (
    <main className="h-screen bg-background text-foreground">
      <div className="flex h-full">
        {/* <Sidebar /> */}

        <section className="flex min-w-0 flex-1 flex-col">
          <Header />

          {/* <ChatArea /> */}
        </section>
      </div>
    </main>
  );
}
