"use client"

import { useState } from "react"
import { MessageSquare, Plus, Code, Zap } from "lucide-react"

export default function Sidebar() {
  const [chats, setChats] = useState([
    { id: 1, title: "React Performance Optimization", active: true },
    { id: 2, title: "Python Error Handling", active: false },
    { id: 3, title: "JavaScript Promises", active: false },
  ])

  const setActiveChat = (id: number) => {
    setChats(
      chats.map((chat) => ({
        ...chat,
        active: chat.id === id,
      })),
    )
  }

  return (
    <div className="sidebar w-64 flex flex-col h-full">
      <div className="p-4 flex items-center gap-2 border-b border-[var(--border)]">
        <Zap className="h-5 w-5 text-[var(--primary)]" />
        <span className="font-bold text-lg">CodeAI</span>
      </div>

      <div className="p-4 rounded-xl">
        <button className="new-chat-button">
          <Plus className="h-4 w-4" />
          <span>New chat</span>
        </button>

        <div className="space-y-1">
          {chats.map((chat) => (
            <div
              key={chat.id}
              className={`chat-item ${chat.active ? "active" : ""}`}
              onClick={() => setActiveChat(chat.id)}
            >
              <MessageSquare className="h-4 w-4" />
              <span className="truncate">{chat.title}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-auto p-4 border-t border-[var(--border)]">
        <div className="flex items-center gap-2 text-sm text-[var(--muted-foreground)]">
          <Code className="h-4 w-4" />
          <span>Code Analysis AI</span>
        </div>
      </div>
    </div>
  )
}
