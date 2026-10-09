const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : "Request failed.";
    throw new Error(detail);
  }
  return data;
}

export const learningApi = {
  modules: () => request("/api/learning/modules"),
  module: (id) => request(`/api/learning/modules/${id}`),
  updateProgress: (id, progress_percent) =>
    request(`/api/learning/modules/${id}/progress`, {
      method: "POST",
      body: JSON.stringify({ progress_percent }),
    }),
  assessments: () => request("/api/learning/assessments"),
  assessment: (id) => request(`/api/learning/assessments/${id}`),
  submitAssessment: (id, answers) =>
    request(`/api/learning/assessments/${id}/attempts`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    }),
  attempts: () => request("/api/learning/attempts"),
  progress: () => request("/api/learning/progress"),
};
