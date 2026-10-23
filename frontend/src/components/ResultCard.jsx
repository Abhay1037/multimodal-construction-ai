import { AlertTriangle, CheckCircle2, ShieldAlert } from "lucide-react";

const STATUS_STYLES = {
  Safe: {
    badge: "bg-green-100 text-green-800",
    bar: "bg-green-500",
    icon: CheckCircle2,
    label: "All clear",
  },
  Warning: {
    badge: "bg-amber-100 text-amber-800",
    bar: "bg-amber-500",
    icon: AlertTriangle,
    label: "Review required",
  },
  Hazardous: {
    badge: "bg-red-100 text-red-800",
    bar: "bg-red-500",
    icon: ShieldAlert,
    label: "Immediate action",
  },
};

export default function ResultCard({ result, analysisType }) {
  if (!result) return null;

  const status = result.status || "Warning";
  const style = STATUS_STYLES[status] || STATUS_STYLES.Warning;
  const StatusIcon = style.icon;

  const confidence = typeof result.confidence_score === "number" ? result.confidence_score : 0;

  return (
    <div className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-200">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-lg font-semibold text-slate-900">Analysis Result</h3>
        <span
          className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-semibold ${style.badge}`}
        >
          <StatusIcon className="h-4 w-4" />
          {status}
        </span>
      </div>

      <p className="mt-3 text-sm text-slate-600">{result.summary}</p>

      <div className="mt-4">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-slate-700">Confidence Score</span>
          <span className="font-semibold text-slate-900">{confidence.toFixed(1)}%</span>
        </div>
        <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-slate-200">
          <div
            className={`h-2 rounded-full ${style.bar}`}
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      <div className="mt-6 grid gap-6 md:grid-cols-2">
        <div>
          <h4 className="font-semibold text-slate-900">Findings</h4>
          {result.findings && result.findings.length > 0 ? (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
              {result.findings.map((finding, index) => (
                <li key={index}>{finding}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-slate-500">No findings recorded.</p>
          )}
        </div>
        <div>
          <h4 className="font-semibold text-slate-900">Action Items</h4>
          {result.action_items && result.action_items.length > 0 ? (
            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-700">
              {result.action_items.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-slate-500">No action items required.</p>
          )}
        </div>
      </div>

      <p className="mt-4 text-xs text-slate-500">Analysis type: {analysisType}</p>
    </div>
  );
}
