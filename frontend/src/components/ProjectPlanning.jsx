import { useState } from "react";
import axios from "axios";
import { CalendarRange, DollarSign, Ruler, Wallet } from "lucide-react";

export default function ProjectPlanning() {
  const [form, setForm] = useState({
    area: "",
    budget: "",
    category: "Residential",
    duration: "",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("/api/plan-estimate", {
        plot_size_sqft: parseFloat(form.area),
        budget_usd: parseFloat(form.budget),
        category: form.category,
        timeline_weeks: parseInt(form.duration, 10) || 12,
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate the construction plan.");
    } finally {
      setLoading(false);
    }
  };

  const feasibilityStyles = {
    Feasible: "bg-green-100 text-green-800",
    Borderline: "bg-amber-100 text-amber-800",
    Infeasible: "bg-red-100 text-red-800",
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
        <h2 className="text-xl font-semibold text-slate-900">Planning &amp; Valuation</h2>
        <p className="mt-1 text-sm text-slate-500">
          Provide plot size, budget and timeline to generate a milestone breakdown and cost feasibility.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <Ruler className="h-4 w-4" /> Area (sq ft)
            </span>
            <input
              type="number"
              name="area"
              min="1"
              step="0.1"
              required
              value={form.area}
              onChange={handleChange}
              placeholder="e.g. 3000"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </label>

          <label className="block">
            <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <Wallet className="h-4 w-4" /> Budget (USD)
            </span>
            <input
              type="number"
              name="budget"
              min="1"
              step="100"
              required
              value={form.budget}
              onChange={handleChange}
              placeholder="e.g. 250000"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Category</span>
            <select
              name="category"
              value={form.category}
              onChange={handleChange}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            >
              <option>Residential</option>
              <option>Commercial</option>
            </select>
          </label>

          <label className="block">
            <span className="flex items-center gap-2 text-sm font-medium text-slate-700">
              <CalendarRange className="h-4 w-4" /> Duration (weeks)
            </span>
            <input
              type="number"
              name="duration"
              min="1"
              required
              value={form.duration}
              onChange={handleChange}
              placeholder="e.g. 24"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
          </label>

          <div className="sm:col-span-2">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-6 py-3 font-semibold text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <DollarSign className="h-5 w-5" />
              {loading ? "Generating Plan..." : "Generate Cost Estimate"}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-700 ring-1 ring-red-200">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
              <p className="text-sm text-slate-500">Estimated Cost</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                ${result.estimated_cost_usd?.toLocaleString()}
              </p>
            </div>
            <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
              <p className="text-sm text-slate-500">Cost per Sq Ft</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                ${result.estimated_cost_per_sqft?.toFixed(2)}
              </p>
            </div>
            <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
              <p className="text-sm text-slate-500">Budget</p>
              <p className="mt-1 text-2xl font-bold text-slate-900">
                ${result.budget_usd?.toLocaleString()}
              </p>
            </div>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-slate-900">Cost Feasibility</h3>
              <span
                className={`rounded-full px-3 py-1 text-sm font-semibold ${
                  feasibilityStyles[result.feasibility] || feasibilityStyles.Borderline
                }`}
              >
                {result.feasibility}
              </span>
            </div>
            <p className="mt-2 text-sm text-slate-600">
              Estimated duration: {result.timeline_weeks} weeks · Category: {result.category}
            </p>
          </div>

          <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
            <h3 className="text-lg font-semibold text-slate-900">Milestone Breakdown</h3>
            <ol className="mt-4 space-y-4">
              {result.milestones?.map((milestone) => (
                <li key={milestone.week} className="rounded-xl bg-slate-50 p-4">
                  <p className="font-semibold text-slate-800">
                    Week {milestone.week}: {milestone.milestone}
                  </p>
                  {milestone.tasks && milestone.tasks.length > 0 && (
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
                      {milestone.tasks.map((task, index) => (
                        <li key={index}>{task}</li>
                      ))}
                    </ul>
                  )}
                </li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}
