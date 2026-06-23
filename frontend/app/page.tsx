export default function Home() {
  return (
    <div className="flex h-screen bg-gray-900 text-white">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 p-4 hidden md:flex flex-col">
        <h2 className="text-xl font-bold mb-4">Chat History</h2>
        <div className="flex-1"></div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        <div className="flex-1 p-4 overflow-y-auto">
          <h1 className="text-2xl text-center mt-10 text-gray-500">
            ChatGPT Clone
          </h1>
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-700">
          <input
            type="text"
            className="w-full p-3 rounded bg-gray-700 focus:outline-none"
            placeholder="Message ChatGPT..."
          />
        </div>
      </main>
    </div>
  );
}
