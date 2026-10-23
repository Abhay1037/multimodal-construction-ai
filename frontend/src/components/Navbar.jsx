import { ClipboardList, HardHat, Image as ImageIcon, ShieldCheck } from "lucide-react";

const TABS = [
  { id: "site", label: "Site Inspection", icon: ShieldCheck },
  { id: "planning", label: "Planning & Valuation", icon: ClipboardList },
  { id: "visualization", label: "AI Visualization", icon: ImageIcon },
];

export default function Navbar({ activeTab, onNavigate }) {
  return (
    <nav className="sticky top-0 z-50 bg-slate-900 text-white shadow-lg">
      <div className="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-orange-500 p-2">
            <HardHat className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold leading-tight">
              Multimodal Construction Intelligence Platform
            </h1>
            <p className="text-xs text-slate-400">
              AI safety · Structural · Planning · Visualization
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => onNavigate(id)}
              className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors ${
                activeTab === id
                  ? "bg-orange-500 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white"
              }`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden sm:inline">{label}</span>
            </button>
          ))}
        </div>
      </div>
    </nav>
  );
}
