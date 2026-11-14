// Copy to your Next.js project, e.g. lib/voterguard-api.ts
// Set NEXT_PUBLIC_API_URL in Vercel (Project > Settings > Environment Variables)
// e.g. https://voterguard-api.onrender.com  (no trailing slash)
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function post(path: string, file: File, extra?: Record<string, string>) {
  const form = new FormData();
  form.append("file", file);
  for (const [k, v] of Object.entries(extra ?? {})) form.append(k, v);
  // Do NOT set Content-Type yourself; the browser adds the multipart boundary.
  const res = await fetch(`${API}${path}`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(typeof err.detail === "string" ? err.detail : `Request failed (${res.status})`);
  }
  return res.json();
}

export const analyzeImage = (file: File) => post("/analyze", file);
export const screenImage = (file: File) => post("/screen", file);
export const addToCollection = (file: File, label: string) => post("/collection", file, { label });

export async function getStats() {
  const res = await fetch(`${API}/stats`);
  if (!res.ok) throw new Error("Could not load stats");
  return res.json();
}

export async function reviewMatch(
  matchId: number,
  disposition: "confirmed_duplicate" | "not_duplicate" | "needs_more_info",
  reviewer: string,
  note?: string
) {
  const res = await fetch(`${API}/matches/${matchId}/review`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ disposition, reviewer, note }),
  });
  if (!res.ok) throw new Error("Review failed");
  return res.json();
}
