import { Plus } from "lucide-react"
import ProjectCard from "@/components/project-card"
import CreateProjectModal from "@/components/create-project-modal"

// Mock project data
const mockProjects = [
  {
    id: "1",
    repoName: "requests",
    authorName: "pfs",
  },
]

export default function Home() {
  return (
    <div className="min-h-screen bg-[#0f0f0f]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white">Мои проекты</h1>
          <CreateProjectModal
            trigger={
              <button className="flex items-center gap-2 px-4 py-2 bg-[#ffd700] text-black font-medium rounded-full hover:bg-[#e6c200] transition-colors">
                <Plus className="h-5 w-5" />
                Создать проект
              </button>
            }
          />
        </div>

        {mockProjects.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <div className="w-20 h-20 rounded-full bg-[rgba(255,215,0,0.1)] flex items-center justify-center mb-4">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-[#ffd700]"
              >
                <path d="m18 16 4-4-4-4" />
                <path d="m6 8-4 4 4 4" />
                <path d="m14.5 4-5 16" />
              </svg>
            </div>
            <h2 className="text-2xl font-bold mb-2 text-white">No projects yet</h2>
            <p className="text-[#a0a0a0] max-w-md mb-8">Create your first project to start analyzing code with AI.</p>
            <CreateProjectModal
              trigger={
                <button className="flex items-center gap-2 px-6 py-3 bg-[#ffd700] text-black font-medium rounded-xl hover:bg-[#e6c200] transition-colors">
                  <Plus className="h-5 w-5" />
                  Create Your First Project
                </button>
              }
            />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockProjects.map((project) => (
              <ProjectCard
                key={project.id}
                id={project.id}
                repoName={project.repoName}
                authorName={project.authorName}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
