import type { EvalRun, Me, PitchState, Project, Submission } from "./types";

function csrfToken(): string {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.method && options.method !== "GET") headers.set("X-CSRFToken", csrfToken());
  if (options.body && !(options.body instanceof FormData)) headers.set("Content-Type", "application/json");
  const response = await fetch(`/api${path}`, { ...options, headers, credentials: "include" });
  if (!response.ok) {
    const text = await response.text();
    throw new ApiError(response.status, text || response.statusText);
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

const post = <T>(path: string, body?: unknown) =>
  request<T>(path, { method: "POST", body: body instanceof FormData ? body : JSON.stringify(body ?? {}) });

export const api = {
  me: () => request<Me>("/me/"),
  projects: () => request<Project[]>("/projects/"),
  createProject: (course: string, title: string) => post<Project>("/projects/", { course, title }),
  upload: (projectId: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return post<Submission>(`/projects/${projectId}/submissions/`, form);
  },
  startRun: (submission: string, mode: EvalRun["mode"]) => post<EvalRun>("/runs/", { submission, mode }),
  runs: (submission: string) => request<EvalRun[]>(`/runs/?submission=${submission}`),
  run: (id: string) => request<EvalRun>(`/runs/${id}/`),
  review: (id: string, overrides: { criterion_score: string; teacher_score: number }[], comment: string) =>
    post<EvalRun>(`/runs/${id}/review/`, { overrides, comment }),
  createPitch: (submission: string) => post<PitchState>("/pitch/sessions/", { submission }),
  pitch: (id: string) => request<PitchState>(`/pitch/sessions/${id}/`),
  pitchNext: (id: string) => post<PitchState>(`/pitch/sessions/${id}/next/`),
  pitchMessage: (id: string, content: string) => post<PitchState>(`/pitch/sessions/${id}/messages/`, { content }),
};
