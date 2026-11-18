import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { EvalRun, Project } from "../api/types";

export default function TeacherPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [runs, setRuns] = useState<Record<string, EvalRun[]>>({});

  useEffect(() => {
    api.projects().then(async (items) => {
      setProjects(items);
      const entries = await Promise.all(
        items
          .filter((p) => p.latest_submission)
          .map(async (p) => [p.id, await api.runs(p.latest_submission!.id)] as const)
      );
      setRuns(Object.fromEntries(entries));
    });
  }, []);

  const startBoth = async (submissionId: string, projectId: string) => {
    await api.startRun(submissionId, "multi_agent");
    await api.startRun(submissionId, "single_ai");
    setRuns({ ...runs, [projectId]: await api.runs(submissionId) });
  };

  return (
    <section>
      <h1>Проекты курса</h1>
      <table>
        <thead>
          <tr>
            <th>Проект</th>
            <th>Источник</th>
            <th>Оценки AI</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {projects.map((project) => (
            <tr key={project.id}>
              <td>{project.title}</td>
              <td>{project.data_source}</td>
              <td>
                {(runs[project.id] ?? []).map((run) => (
                  <Link key={run.id} to={`/runs/${run.id}`} className="pill">
                    {run.mode === "multi_agent" ? "Агенты" : "1 AI"}: {run.total_score ?? run.status}
                    {run.review ? " ✓" : ""}
                  </Link>
                ))}
              </td>
              <td>
                {project.latest_submission && (
                  <button onClick={() => startBoth(project.latest_submission!.id, project.id)}>Сравнить: агенты и 1 AI</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
