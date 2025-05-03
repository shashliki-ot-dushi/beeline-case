import Link from "next/link"
import { GitFork } from "lucide-react"

interface ProjectCardProps {
  id: string
  repoName: string
  authorName: string
}

export default function ProjectCard({ id, repoName, authorName }: ProjectCardProps) {
  return (
    <Link href={`/projects/${id}`} className="block">
      <div className="bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl p-6 hover:border-[#ffd700] transition-colors shadow-md hover:shadow-lg">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-md bg-[rgba(255,215,0,0.1)] flex items-center justify-center">
            <GitFork className="h-5 w-5 text-[#ffd700]" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">{repoName}</h3>
            <p className="text-sm text-[#a0a0a0]">{authorName}</p>
          </div>
        </div>
        <div className="flex justify-between items-center">
          <div className="flex -space-x-2">
            <div className="w-7 h-7 rounded-full bg-[#2a2a2a] flex items-center justify-center text-xs text-white">
              3
            </div>
            <div className="w-7 h-7 rounded-full bg-[#333] flex items-center justify-center text-xs text-white">+</div>
          </div>
          <span className="text-xs text-[#a0a0a0]">3 chats</span>
        </div>
      </div>
    </Link>
  )
}
