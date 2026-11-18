export type Role = "student" | "instructor" | "expert" | "admin";

export interface Me {
  id: string;
  name: string;
  is_superuser: boolean;
  courses: { id: string; title: string; role: Role }[];
}

export interface Submission {
  id: string;
  version: number;
  status: string;
  documents: { id: string; original_name: string; file_type: string }[];
}

export interface Project {
  id: string;
  course: string;
  title: string;
  description: string;
  data_source: "synthetic" | "educational" | "past_work";
  latest_submission: Submission | null;
}

export interface Evidence {
  id: number;
  slide_no: number | null;
  quote: string;
  verified: boolean;
}

export interface CriterionScore {
  id: string;
  criterion_name: string;
  weight: string;
  agent_type: string;
  ai_score: number;
  teacher_score: number | null;
  justification: string;
  missing: string[];
  evidence: Evidence[];
}

export interface EvalRun {
  id: string;
  mode: "multi_agent" | "single_ai";
  status: "queued" | "running" | "done" | "failed";
  model_name: string;
  total_score: string | null;
  duration_ms: number | null;
  error: string;
  scores: CriterionScore[];
  review: { final_score: string; comment: string; status: string } | null;
  created_at: string;
}

export interface PitchState {
  id: string;
  status: "created" | "pitch" | "qa" | "feedback" | "finished";
  stage: string | null;
  planned_sec: number | null;
  remaining_sec: number | null;
  questions: string[];
  feedback: { strengths?: string[]; remarks?: string[]; slide_refs?: number[] };
  stages: { stage: string; planned_sec: number; actual_sec: number | null; auto_ended: boolean }[];
}
