import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import type { EvalRun } from "../api/types";

export default function ReportPage({ isTeacher }: { isTeacher: boolean }) {
  const { runId } = useParams();
  const [run, setRun] = useState<EvalRun | null>(null);
  const [overrides, setOverrides] = useState<Record<string, number>>({});
  const [comment, setComment] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!runId) return;
    let timer: number;
    const poll = async () => {
      const data = await api.run(runId);
      setRun(data);
      if (data.status === "queued" || data.status === "running") timer = window.setTimeout(poll, 2000);
    };
    poll();
    return () => window.clearTimeout(timer);
  }, [runId]);

  if (!run) return <p>Загрузка…</p>;
  if (run.status === "failed") return <p className="error">Ошибка оценки: {run.error}</p>;
  if (run.status !== "done") return <p>AI анализирует презентацию…</p>;

  const approve = async () => {
    setError("");
    try {
      const items = Object.entries(overrides).map(([criterion_score, teacher_score]) => ({ criterion_score, teacher_score }));
      setRun(await api.review(run.id, items, comment));
    } catch (e) {
      setError((e as Error).message);
    }
  };

  return (
    <section>
      <h1>Отчёт AI-оценки</h1>
      <p className="muted">
        Режим: {run.mode === "multi_agent" ? "5 агентов" : "один AI-ассистент"} · модель {run.model_name} · {run.duration_ms} мс
      </p>
      <p className="score">Предварительный балл: {run.total_score} / 5</p>
      {run.review && (
        <p className="success">
          Утверждено преподавателем: {run.review.final_score} / 5. {run.review.comment}
        </p>
      )}
      {run.scores.map((score) => (
        <article key={score.id} className="card">
          <div className="row between">
            <h2>{score.criterion_name}</h2>
            <span className="pill">
              AI: {score.ai_score}
              {score.teacher_score ? ` → ${score.teacher_score}` : ""}
            </span>
          </div>
          <p>{score.justification}</p>
          {score.evidence.map((ev) => (
            <blockquote key={ev.id} className={ev.verified ? "verified" : "unverified"}>
              «{ev.quote}» — слайд {ev.slide_no ?? "?"} {ev.verified ? "✓ найдено в документе" : "⚠ не подтверждено"}
            </blockquote>
          ))}
          {score.missing.length > 0 && <p className="muted">Не раскрыто: {score.missing.join("; ")}</p>}
          {isTeacher && !run.review && (
            <label>
              Балл преподавателя:{" "}
              <select
                value={overrides[score.id] ?? score.ai_score}
                onChange={(e) => setOverrides({ ...overrides, [score.id]: Number(e.target.value) })}
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n}>{n}</option>
                ))}
              </select>
            </label>
          )}
        </article>
      ))}
      {isTeacher && !run.review && (
        <div className="card">
          <textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Комментарий для студента" />
          <button onClick={approve}>Утвердить оценку</button>
          {error && <p className="error">{error}</p>}
        </div>
      )}
    </section>
  );
}
