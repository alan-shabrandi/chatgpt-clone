import { Bot, Send, User } from "lucide-react";
import React, { useEffect, useRef, useState } from "react";

const ChatArea = () => {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>(
    [],
  );
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    setTimeout(() => {
      const aiResponse = {
        role: "assistant",
        content: "من یک هوش مصنوعی هستم! (در مراحل بعدی به FastAPI وصل می‌شوم)",
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1000);
  };
  return (
    <main className="flex-1 flex flex-col">
      <div className="flex-1 p-4 overflow-y-auto space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {msg.role === "assistant" && (
              <div className="p-2 bg-gray-600 rounded-full h-fit">
                <Bot size={20} />
              </div>
            )}
            <div
              className={`p-4 rounded-xl max-w-[80%] ${msg.role === "user" ? "bg-blue-600" : "bg-gray-700"}`}
            >
              {msg.content}
            </div>
            {msg.role === "user" && (
              <div className="p-2 bg-blue-700 rounded-full h-fit">
                <User size={20} />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

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
          className="bg-blue-600 p-3 rounded-lg hover:bg-blue-700 transition"
        >
          <Send size={20} />
        </button>
      </div>
    </main>
  );
};

export default ChatArea;
