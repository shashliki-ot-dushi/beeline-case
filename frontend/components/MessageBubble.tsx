import React from 'react'
import { CodePanelTrigger } from '../types'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

interface MessageBubbleProps {
  message: Message
  onViewCode: (code: string, lang: string, title: string) => void
  onDiagramClick: () => void
}

export function MessageBubble({ message, onViewCode, onDiagramClick }: MessageBubbleProps) {
  // Разбиваем по блокам ```
  const parts = message.content.split('```')

  return (
    <div
      className={`mb-6 flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-3xl rounded-2xl px-4 py-3 ${
          message.role === 'user' ? 'bg-[#ffd700] text-black' : 'bg-[#1a1a1a] text-white'
        }`}
        style={{ maxWidth: '80%' }}
      >
        {parts.map((part, idx) => {
          if (idx % 2 === 0) {
            // Обычный текст
            return <p key={idx} className="whitespace-pre-wrap mb-2">{part}</p>
          }
          // Код или диаграмма
          const [lang, ...rest] = part.split('\n')
          const code = rest.join('\n')

          if (lang.trim() === 'mermaid') {
            return (
              <div key={idx} onClick={onDiagramClick} className="cursor-pointer">
                {/* SVG-диаграмма */}
                <div className="p-4 bg-[#121212] rounded-md">
                  <p className="text-center text-[#a0a0a0] text-sm mb-2">Click to view implementation</p>
                  {/* Здесь упрощённая отрисовка */}
                </div>
              </div>
            )
          }

          // Обычный кодовый блок
          return (
            <div key={idx} className="my-4 rounded-md overflow-hidden">
              <div className="bg-[#1e1e1e] px-4 py-1.5 text-xs text-[#a0a0a0] flex justify-between items-center">
                <span>{lang}</span>
                <button
                  className="flex items-center gap-1 hover:text-white transition-colors"
                  onClick={() => onViewCode(code, lang, 'Code Example')}
                >
                  View code
                </button>
              </div>
              <pre className="p-4 overflow-x-auto bg-[#121212] text-sm">
                <code>{code}</code>
              </pre>
            </div>
          )
        })}
      </div>
    </div>
  )
}