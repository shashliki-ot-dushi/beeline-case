'use client'

import { useState, useEffect, useRef } from 'react'
import { BarChart2, LineChart, PieChart } from 'lucide-react'

export default function ProjectCharts() {
  const [activeChart, setActiveChart] = useState<'overview' | 'performance' | 'dependencies'>('overview')
  const [repoUrl, setRepoUrl] = useState<string>('')
  const [diagramText, setDiagramText] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const mermaidRef = useRef<HTMLDivElement>(null)

  // Отключаем SSR
  if (typeof window === 'undefined') return null

  // Преобразуем C4-модель в синтаксис Mermaid
  function buildMermaid(c4: {
    containers: { id: string; name: string }[]
    components: { id: string; name: string }[]
    relationships: { source: string; destination: string; description: string }[]
  }): string {
    let md = 'graph TB\n'
    c4.containers.forEach(c => {
      const nodeId = c.id.replace(/[:\\/.]/g, '_')
      md += `  ${nodeId}["${c.name}"]\n`
    })
    c4.components.forEach(comp => {
      const nodeId = comp.id.replace(/[:\\/.]/g, '_')
      md += `  ${nodeId}["${comp.name}"]\n`
    })
    c4.relationships.forEach(rel => {
      const from = rel.source.replace(/[:\\/.]/g, '_')
      const to = rel.destination.replace(/[:\\/.]/g, '_')
      md += `  ${from} -->|${rel.description}| ${to}\n`
    })
    return md
  }

  // Рендерим Mermaid на клиенте с панорамированием и зумом
  useEffect(() => {
    if (!diagramText || !mermaidRef.current) return
    const renderMermaid = async () => {
      try {
        const mermaidLib = (await import('mermaid')).default
        mermaidLib.initialize({
          startOnLoad: false,
          theme: 'dark',
          securityLevel: 'loose',
          flowchart: { useMaxWidth: true }
        })
        const { svg, bindFunctions } = await mermaidLib.render('diagram', diagramText)
        if (!mermaidRef.current) return
        mermaidRef.current.innerHTML = svg
        const svgEl = mermaidRef.current.querySelector('svg')
        if (svgEl && bindFunctions) bindFunctions(svgEl)
        const panzoom = (await import('panzoom')).default
        if (svgEl) panzoom(svgEl, { maxZoom: 20, minZoom: 0.1, zoomDoubleClickSpeed: 1, smoothScroll: true, bounds: true, boundsPadding: 0.1 })
      } catch (err) {
        console.error('Mermaid render error:', err)
      }
    }
    renderMermaid()
  }, [diagramText])

  // Запрос к API и генерация диаграммы
  async function fetchDiagram() {
    if (!repoUrl) return
    setLoading(true)
    try {
      const resp = await fetch('http://localhost:8000/api/diagram', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl }),
      })
      if (!resp.ok) throw new Error(`Ошибка ${resp.status}`)
      const c4 = await resp.json()
      setDiagramText(buildMermaid(c4))
      setActiveChart('dependencies')
    } catch (e) {
      console.error('Не удалось загрузить C4-модель:', e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-7xl mx-auto">
        {/* Ввод URL */}
        <div className="mb-6 flex">
          <input
            type="text"
            value={repoUrl}
            onChange={e => setRepoUrl(e.target.value)}
            className="flex-1 px-4 py-2 rounded-l-xl bg-[#2a2a2a] text-white border border-[#444]"
            placeholder="https://github.com/user/repo.git"
          />
          <button
            onClick={fetchDiagram}
            disabled={loading}
            className="px-4 py-2 rounded-r-xl bg-[#ffd700] text-black"
          >
            {loading ? 'Loading...' : 'Load Dependencies'}
          </button>
        </div>

        {/* Кнопки переключения */}
        <div className="mb-6 flex space-x-2">
          <button
            onClick={() => setActiveChart('overview')}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 ${
              activeChart === 'overview'
                ? 'bg-[#2a2a2a] text-white'
                : 'text-[#a0a0a0] hover:bg-[#1a1a1a] hover:text-white'
            }`}
          >
            <BarChart2 className="h-4 w-4" />
            <span>Overview</span>
          </button>
          <button
            onClick={() => setActiveChart('performance')}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 ${
              activeChart === 'performance'
                ? 'bg-[#2a2a2a] text-white'
                : 'text-[#a0a0a0] hover:bg-[#1a1a1a] hover:text-white'
            }`}
          >
            <LineChart className="h-4 w-4" />
            <span>Performance</span>
          </button>
          <button
            onClick={fetchDiagram}
            disabled={loading}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 ${
              activeChart === 'dependencies'
                ? 'bg-[#2a2a2a] text-white'
                : 'text-[#a0a0a0] hover:bg-[#1a1a1a] hover:text-white'
            }`}
          >
            <PieChart className="h-4 w-4" />
            <span>{loading ? '...' : 'Dependencies'}</span>
          </button>
        </div>

        {/* Диаграмма */}
        {activeChart === 'dependencies' && (
          <div className="bg-[#1a1a1a] rounded-xl p-6 shadow-md animate-fadeIn">
            <h3 className="text-lg font-medium mb-4 text-white">Dependency Graph</h3>
            {loading ? (
              <div className="text-center text-white">Loading diagram...</div>
            ) : (
              <div
                ref={mermaidRef}
                className="overflow-auto"
                style={{ width: '100%', height: '800px', cursor: 'move' }}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

/* Установи пакеты:
   npm install mermaid panzoom
   yarn add mermaid panzoom
*/
