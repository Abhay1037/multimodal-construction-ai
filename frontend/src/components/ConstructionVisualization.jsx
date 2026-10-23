import { useState } from "react";
import axios from "axios";
import { Building2, Image as ImageIcon, RefreshCw, Wand2 } from "lucide-react";

const SAMPLE_PROMPTS = [
  "Modern 3-story concrete building with solar panels",
  "Single-family residential house with wood framing and large windows",
  "Commercial concrete structure with glass facade and rooftop garden",
];

export default function ConstructionVisualization() {
  const [prompt, setPrompt] = useState("");
  const [imageUrl, setImageUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const trimmed = prompt.trim();
    if (!trimmed) {
      setError("Please enter a construction visualization prompt.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("/api/generate-visualization", { prompt: trimmed });
      setImageUrl(response.data.image_url);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate the visualization.");
    } finally {
      setLoading(false);
    }
  };

  const handleSurpriseMe = () => {
    const next = SAMPLE_PROMPTS[Math.floor(Math.random() * SAMPLE_PROMPTS.length)];
    setPrompt(next);
  };

  const handleRegenerate = async () => {
    const trimmed = prompt.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("/api/generate-visualization", { prompt: trimmed });
      setImageUrl(response.data.image_url);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate the visualization.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
        <h2 className="flex items-center gap-2 text-xl font-semibold text-slate-900">
          <ImageIcon className="h-6 w-6 text-orange-500" /> AI Construction Visualization
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Describe your construction concept and let the Flux model generate an architectural preview.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4 sm:flex-row">
          <input
            type="text"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="e.g. Modern 3-story concrete building with solar panels"
            className="w-full flex-1 rounded-lg border border-slate-300 px-4 py-3 text-sm"
          />
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-slate-900 px-6 py-3 font-semibold text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <Wand2 className="h-5 w-5" />
              {loading ? "Generating..." : "Generate"}
            </button>
            <button
              type="button"
              onClick={handleRegenerate}
              disabled={loading}
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 px-4 py-3 font-semibold text-slate-700 transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RefreshCw className={`h-5 w-5 ${loading ? "animate-spin" : ""}`} />
              Retry
            </button>
          </div>
        </form>

        <div className="mt-4 flex flex-wrap gap-2">
          {SAMPLE_PROMPTS.map((sample) => (
            <button
              key={sample}
              type="button"
              onClick={() => setPrompt(sample)}
              className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-200"
            >
              {sample}
            </button>
          ))}
        </div>

        {error && (
          <div className="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-700 ring-1 ring-red-200">
            {error}
          </div>
        )}
      </div>

      {imageUrl && (
        <div className="overflow-hidden rounded-2xl bg-white shadow-md ring-1 ring-slate-200">
          <div className="flex items-center gap-2 border-b border-slate-100 bg-slate-50 px-4 py-3">
            <Building2 className="h-4 w-4 text-orange-500" />
            <p className="text-sm font-medium text-slate-700 truncate">Concept preview</p>
          </div>
          <img src={imageUrl} alt={prompt} className="w-full object-cover" />
          <div className="p-4">
            <p className="text-xs text-slate-500">Prompt: {prompt}</p>
          </div>
        </div>
      )}
    </div>
  );
}
