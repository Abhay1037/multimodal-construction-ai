import { useState } from "react";
import Navbar from "./components/Navbar";
import SiteInspection from "./components/SiteInspection";
import ProjectPlanning from "./components/ProjectPlanning";
import ConstructionVisualization from "./components/ConstructionVisualization";

export default function App() {
  const [activeTab, setActiveTab] = useState("site");

  return (
    <div className="min-h-screen bg-slate-100">
      <Navbar activeTab={activeTab} onNavigate={setActiveTab} />
      <main className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        {activeTab === "site" && <SiteInspection />}
        {activeTab === "planning" && <ProjectPlanning />}
        {activeTab === "visualization" && <ConstructionVisualization />}
      </main>
    </div>
  );
}
