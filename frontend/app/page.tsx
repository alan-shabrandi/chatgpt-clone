"use client";

import { useState } from "react";

export default function Home() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    [],
  );
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) return;

    // اضافه کردن پیام کاربر به لیست
    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar - بدون تغییر */}
      <aside className="w-64 bg-gray-800 p-4 hidden md:flex flex-col">
        <h2 className="text-xl font-bold mb-4">Chat History</h2>
      </aside>

      <main className="flex-1 flex flex-col">
        {/* نمایش لیست پیام‌ها */}
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`p-3 rounded ${msg.role === "user" ? "bg-blue-600 self-end" : "bg-gray-700"}`}
            >
              {msg.content}
            </div>
          ))}
        </div>

        {/* بخش ورودی */}
        <div className="p-4 border-t border-gray-700 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            type="text"
            className="flex-1 p-3 rounded bg-gray-700 focus:outline-none"
            placeholder="Message ChatGPT..."
          />
          <button
            onClick={handleSend}
            className="bg-blue-600 px-4 py-2 rounded"
          >
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
