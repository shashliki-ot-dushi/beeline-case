import ChatInterface from "@/components/chat-interface"

export default function Home() {
  return (
    <div className="flex h-screen bg-[#0f0f0f]">
      <div className="w-64 bg-[#1a1a1a] border-r border-[#2a2a2a]">
        <div className="p-4 flex items-center gap-2 border-b border-[#2a2a2a]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-5 w-5 text-[#ffd700]"
          >
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          <span className="font-bold text-lg text-white">CodeAI</span>
        </div>

        <div className="p-4">
          <button className="flex items-center gap-2 w-full p-3 border border-[#2a2a2a] rounded-xl text-white hover:bg-[#2a2a2a] transition-colors">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-4 w-4"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>Новый чат</span>
          </button>

          <div className="mt-4 space-y-1">
            <div className="flex items-center gap-2 p-3 rounded-xl bg-[#2a2a2a] text-white hover:text-[#FED305] transition-colors">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <span className="truncate">Чат 1</span>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-xl text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-[#FED305] transition-colors">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <span className="truncate">Чат 2</span>
            </div>

            <div className="flex items-center gap-2 p-3 rounded-xl text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-[#FED305] transition-colors">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-4 w-4"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <span className="truncate">Чат 3</span>
            </div>
          </div>
        </div>

        <div className="absolute bottom-0 left-0 w-64 p-4 border-t border-[#2a2a2a]">
          <div className="flex items-center gap-2 text-sm text-[#a0a0a0]">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-4 w-4"
            >
              <path d="m18 16 4-4-4-4" />
              <path d="m6 8-4 4 4 4" />
              <path d="m14.5 4-5 16" />
            </svg>
            <span>ИИ Анализ кода</span>
          </div>
        </div>
      </div>

      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatInterface />
      </main>
    </div>
  )
}
