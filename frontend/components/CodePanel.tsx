import React from 'react'
import { ChevronRight } from 'lucide-react'
import { CopyButton } from './CopyButton'

interface CodePanelProps {
  isOpen: boolean
  width: number
  title: string
  code: string
  onClose: () => void
  onStartResize: (e: React.MouseEvent) => void
}

export function CodePanel({ isOpen, width, title, code, onClose, onStartResize }: CodePanelProps) {
  if (!isOpen) return null
  return (
    <div
      className="fixed top-0 right-0 h-full bg-[#121212] border-l border-[#2a2a2a] shadow-xl z-10 flex flex-col transition-all duration-300"
      style={{ width: `${width}px` }}
    >
      {/* Полоса для ресайза */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 cursor-ew-resize hover:bg-[#ffd700]"
        onMouseDown={onStartResize}
      ></div>

      {/* Заголовок и кнопка закрытия */}
      <div className="flex items-center justify-between p-4 border-b border-[#2a2a2a]">
        <div className="flex items-center">
          <button onClick={onClose} className="mr-3 hover:bg-[#2a2a2a] p-1 rounded-md">
            <ChevronRight className="h-5 w-5" />
          </button>
          <h3 className="font-medium text-white">{title}</h3>
        </div>
        <CopyButton code={code} />
      </div>

      {/* Блок с кодом */}
      <div className="flex-1 overflow-auto p-4">
        <pre className="text-sm">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  )
}