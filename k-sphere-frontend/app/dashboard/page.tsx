import { AppSidebar } from "@/components/app-sidebar"

export default function DashboardPage() {
  return (
    <div className="flex h-screen">
      <AppSidebar />

      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
            <p className="mt-2 text-muted-foreground">System overview and knowledge base statistics</p>
          </div>
        </div>
      </main>
    </div>
  )
}
