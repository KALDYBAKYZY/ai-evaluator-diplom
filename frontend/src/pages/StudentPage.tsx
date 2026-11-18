import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import type { EvalRun, Me, Project } from "../api/types";

export default function StudentPage({ me }: { me: Me }) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();
  const course = me.courses[0];

  const load = () => api.projects().then(setProjects).catch((e) => setMessage(e.message));
  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    if (!course) return setMessage("Нет курса. Откройте приложение из Canvas.");
    if (!title.trim()) return setMessage("Введите название проекта");
    await api.createProject(course.id, title.trim());
    setTitle("");
    load();
  };

  const upload = async (project: Project, file?: File) => {
    if (!file) return;
    setMessage("Загрузка и извлечение текста…");
    try {
      await api.upload(project.id, file);
      setMessage("Файл загружен");
      load();
    } catch (e) {
      setMessage((e as Error).message);
    }
  };

  const evaluate = async (submissionId: string, mode: EvalRun["mode"]) => {
    const run = await api.startRun(submissionId, mode);
    navigate(`/runs/${run.id}`);
  };

  return (
    <section>
      <h1>Мои стартап-проекты</h1>
      <div className="row">
        <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Название проекта" />
        <button onClick={create}>Создать</button>
      </div>
      {message && <p className="muted">{message}</p>}
      {projects.map((project) => (
        <article key={project.id} className="card">
          <h2>{project.title}</h2>
          <label className="upload">
            Загрузить презентацию (PDF/PPTX)
            <input type="file" accept=".pdf,.pptx" onChange={(e) => upload(project, e.target.files?.[0])} />
          </label>
          {project.latest_submission ? (
            <div className="row">
              <span className="muted">
                Версия {project.latest_submission.version}: {project.latest_submission.documents[0]?.original_name}
              </span>
              <button onClick={() => evaluate(project.latest_submission!.id, "multi_agent")}>AI-оценка</button>
              <Link className="button secondary" to={`/pitch/${project.latest_submission.id}`}>
                Тренировка питча
              </Link>
            </div>
          ) : (
            <p className="muted">Файл ещё не загружен</p>
          )}
        </article>
      ))}
    </section>
  );
}
