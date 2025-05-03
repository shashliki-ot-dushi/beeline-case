import React, { useRef, useEffect } from 'react'
import { MessageBubble } from './MessageBubble'
import { Message } from '../types'

interface MessageListProps {
  messages: Message[]
  onViewCode: (code: string, lang: string, title: string) => void
  onDiagramClick: () => void
}

export function MessageList({ messages, onViewCode, onDiagramClick }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-center text-[#a0a0a0]">
          <img src="https://static.beeline.ru/upload/dpcupload/contents/342/avatarbee_2704.svg" className="pb-10 transform scale-[1.5`]"></img>
          <h2 className="text-2xl font-bold mb-2 text-white">ИИ анализ кода</h2>
          <p>Upload your code or paste snippets to get AI-powered analysis.</p>
        </div>
      ) : (
        messages.map(msg => (
          <MessageBubble
            key={msg.id}
            message={msg}
            onViewCode={onViewCode}
            onDiagramClick={onDiagramClick}
          />
        ))
      )}
      <div ref={endRef} />
    </div>
  )
}