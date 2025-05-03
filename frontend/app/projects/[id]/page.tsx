"use client"

import { useState } from "react"
import Link from "next/link"
import { ChevronLeft, Plus, MessageSquare, BarChart2, FileText } from "lucide-react"
import { ChatInterface } from "@/components/chat-interface"
import ProjectCharts from "@/components/project-charts"
import ProjectDocumentation from "@/components/project-documentation"

// Mock chat data
const mockChats = [
  { id: "1", title: "Чат 1" },
  { id: "2", title: "Чат 2" },
  { id: "3", title: "Чат 3" },
]

type TabType = "chat" | "charts" | "documentation"

export default function ProjectPage({ params }: { params: { id: string } }) {
  const [chats, setChats] = useState(mockChats)
  const [activeChat, setActiveChat] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>("chat")

  const createNewChat = () => {
    const newChat = {
      id: (chats.length + 1).toString(),
      title: `Чат ${chats.length + 1}`,
    }
    setChats([...chats, newChat])
    setActiveChat(newChat.id)
    setActiveTab("chat") // Switch to chat tab when creating a new chat
  }

  return (
    <div className="flex h-screen bg-[#0f0f0f]">
      {/* Sidebar - only visible in chat tab */}
      {activeTab === "chat" && (
        <div className="w-64 bg-[#1a1a1a] border-r border-[#2a2a2a]">
          <div className="p-4 flex items-center gap-2 border-b border-[#2a2a2a]">
            <Link href="/" className="flex items-center gap-2 text-[#a0a0a0] hover:text-white transition-colors">
              <ChevronLeft className="h-5 w-5" />
              <span className="font-medium">Вернуться к проектам</span>
            </Link>
          </div>

          <div className="p-4">
            <button
              onClick={createNewChat}
              className="flex items-center gap-2 w-full p-3 border border-[#2a2a2a] rounded-xl text-white hover:bg-[#2a2a2a] transition-colors"
            >
              <Plus className="h-4 w-4" />
              <span>Создать чат</span>
            </button>

            <div className="mt-4 space-y-1">
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`flex items-center gap-2 p-3 rounded-xl cursor-pointer transition-colors ${
                    activeChat === chat.id
                      ? "bg-[#2a2a2a] text-white"
                      : "text-[#a0a0a0] hover:bg-[#2a2a2a] hover:text-[#FED305]"
                  }`}
                  onClick={() => setActiveChat(chat.id)}
                >
                  <MessageSquare className="h-4 w-4" />
                  <span className="truncate">{chat.title}</span>
                </div>
              ))}
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
              <span>ИИ анализ кода</span>
            </div>
          </div>
        </div>
      )}

      <main className={`flex-1 flex flex-col overflow-hidden ${activeTab !== "chat" ? "ml-0" : ""}`}>
        {/* Project header with tabs */}
        <div className="border-b border-[#2a2a2a] bg-[#1a1a1a]">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-3">
              {activeTab !== "chat" && (
                <Link href="/" className="text-[#a0a0a0] hover:text-white transition-colors mr-2">
                  <ChevronLeft className="h-5 w-5" />
                </Link>
              )}
              <h1 className="text-xl font-semibold text-white">Сведения о проекте</h1>
            </div>
          </div>

          <div className="flex px-6">
            <button
              onClick={() => setActiveTab("chat")}
              className={`px-4 py-3 text-sm font-medium flex items-center gap-1.5 transition-colors border-b-2 ${
                activeTab === "chat"
                  ? "border-[#ffd700] text-white"
                  : "border-transparent text-[#a0a0a0] hover:text-white"
              }`}
            >
              <MessageSquare className="h-4 w-4" />
              Чат
            </button>
            <button
              onClick={() => setActiveTab("charts")}
              className={`px-4 py-3 text-sm font-medium flex items-center gap-1.5 transition-colors border-b-2 ${
                activeTab === "charts"
                  ? "border-[#ffd700] text-white"
                  : "border-transparent text-[#a0a0a0] hover:text-white"
              }`}
            >
              <BarChart2 className="h-4 w-4" />
              Диаграммы
            </button>
            <button
              onClick={() => setActiveTab("documentation")}
              className={`px-4 py-3 text-sm font-medium flex items-center gap-1.5 transition-colors border-b-2 ${
                activeTab === "documentation"
                  ? "border-[#ffd700] text-white"
                  : "border-transparent text-[#a0a0a0] hover:text-white"
              }`}
            >
              <FileText className="h-4 w-4" />
              Документация
            </button>
          </div>
        </div>

        {/* Tab content with transitions */}
        <div className="flex-1 overflow-hidden bg-gradient-radial">
          <div
            className={`transition-opacity duration-300 h-full ${activeTab === "chat" ? "opacity-100" : "opacity-0 hidden"}`}
          >
            {activeTab === "chat" &&
              (activeChat ? (
                <ChatInterface />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-4">
                  <div className="relative">
                    <img src="https://static.beeline.ru/upload/dpcupload/contents/342/avatarbee_2704.svg" className="pb-10 transform scale-[1.5`]"></img>
                  </div>
                  <h2 className="text-2xl font-bold mb-2 text-white">Выберите или создайте чат</h2>
                  <p className="text-[#a0a0a0] max-w-md mb-8">
                  Выберите существующий чат на боковой панели или создайте новый, чтобы начать анализ кода.
                  </p>
                  <button
                    onClick={createNewChat}
                    className="flex items-center gap-2 px-6 py-3 bg-[#ffd700] text-black font-medium rounded-xl hover:bg-[#e6c200] transition-colors"
                  >
                    <Plus className="h-5 w-5" />
                    Создать чат
                  </button>
                </div>
              ))}
          </div>

          <div
            className={`transition-opacity duration-300 h-full ${activeTab === "charts" ? "opacity-100" : "opacity-0 hidden"}`}
          >
            {activeTab === "charts" && <ProjectCharts />}
          </div>

          <div
            className={`transition-opacity duration-300 h-full ${activeTab === "documentation" ? "opacity-100" : "opacity-0 hidden"}`}
          >
            {activeTab === "documentation" && <ProjectDocumentation />}
          </div>
        </div>
      </main>
    </div>
  )
}
