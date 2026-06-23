"use client";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";

export default function Home() {
  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <Sidebar />
      <ChatArea />
    </div>
  );
}
