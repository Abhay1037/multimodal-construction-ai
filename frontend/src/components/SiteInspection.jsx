import { useState } from "react";
import axios from "axios";
import { CloudUpload, ScanSearch, ShieldCheck, Stethoscope } from "lucide-react";
import ResultCard from "./ResultCard";

const ANALYSIS_TYPES = [
  { value: "safety_monitoring", label: "PPE Safety Compliance", icon: ShieldCheck },
  { value: "crack_detection", label: "Crack & Structural Damage", icon: Stethoscope },
];

export default function SiteInspection() {
  const [file, setFile] = useState(null);
  const [analysisType, setAnalysisType] = useState("safety_monitoring");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const handleFileChange = (event) => {
    const selected = event.target.files?.[0];
    setFile(selected || null);
    setError(null);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError("Please select a construction photo to upload first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", file);
    formData.append("analysis_type", analysisType);

    setLoading(true);
    setError(null);
    try {
      const response = await axios.post("/api/analyze-site", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setAnalysis(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail || err.response?.data?.message || "Site analysis failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
        <h2 className="text-xl font-semibold text-slate-900">Site Inspection</h2>
        <p className="mt-1 text-sm text-slate-500">
          Upload a construction site photo and let LLaMA analyze safety compliance or structural cracks.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-6">
          <div className="rounded-xl border-2 border-dashed border-slate-300 p-8 text-center">
            <CloudUpload className="mx-auto h-10 w-10 text-slate-400" />
            <p className="mt-3 text-sm font-medium text-slate-700">Drop a construction photo here or</p>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="mt-3 block w-full text-sm text-slate-500 file:mr-4 file:rounded-lg file:border-0 file:bg-orange-500 file:px-4 file:py-2 file:text-white hover:file:bg-orange-600"
            />
            {file && (
              <p className="mt-2 text-xs text-slate-500">Selected: {file.name}</p>
            )}
          </div>

          <div>
            <p className="text-sm font-medium text-slate-700">Analysis Type</p>
            <div className="mt-2 grid gap-3 sm:grid-cols-2">
              {ANALYSIS_TYPES.map(({ value, label, icon: Icon }) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setAnalysisType(value)}
                  className={`flex items-center gap-3 rounded-xl border p-4 text-left transition-colors ${
                    analysisType === value
                      ? "border-orange-500 bg-orange-50"
                      : "border-slate-200 bg-white hover:bg-slate-50"
                  }`}
                >
                  <Icon className={`h-5 w-5 ${analysisType === value ? "text-orange-500" : "text-slate-400"}`} />
                  <span className="text-sm font-medium text-slate-800">{label}</span>
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center gap-2 rounded-lg bg-slate-900 px-6 py-3 font-semibold text-white transition-colors hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <ScanSearch className="h-5 w-5" />
            {loading ? "Analyzing..." : "Run AI Site Analysis"}
          </button>
        </form>

        {error && (
          <div className="mt-6 rounded-lg bg-red-50 p-4 text-sm text-red-700 ring-1 ring-red-200">
            {error}
          </div>
        )}
      </div>

      {analysis && (
        <ResultCard
          result={analysis.result}
          analysisType={analysis.analysis_type?.replace("_", " ")}
        />
      )}
    </div>
  );
}
