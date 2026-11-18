import { useEffect, useState } from "react";
import { Link, Navigate, Route, Routes } from "react-router-dom";
import { api } from "./api/client";
import type { Me } from "./api/types";
import StudentPage from "./pages/StudentPage";
import TeacherPage from "./pages/TeacherPage";
import ReportPage from "./pages/ReportPage";
import PitchPage from "./pages/PitchPage";

export default function App() {
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.me().then(setMe).catch(() => setError("Войдите через Canvas или /admin/"));
  }, []);

  if (error) {
    return (
      <main className="container">
        <h1>AI Startup Evaluator</h1>
        <p>{error}</p>
        <a className="button" href="/admin/login/?next=/">Войти (режим разработки)</a>
      </main>
    );
  }
  if (!me) return <main className="container">Загрузка…</main>;

  const isTeacher = me.is_superuser || me.courses.some((c) => c.role === "instructor" || c.role === "admin");

  return (
    <>
      <header className="topbar">
        <strong>AI Startup Evaluator</strong>
        <nav>
          <Link to="/student">Студент</Link>
          {isTeacher && <Link to="/teacher">Преподаватель</Link>}
        </nav>
        <span>{me.name}</span>
      </header>
      <main className="container">
        <Routes>
          <Route path="/" element={<Navigate to={isTeacher ? "/teacher" : "/student"} replace />} />
          <Route path="/student" element={<StudentPage me={me} />} />
          <Route path="/teacher" element={<TeacherPage />} />
          <Route path="/runs/:runId" element={<ReportPage isTeacher={isTeacher} />} />
          <Route path="/pitch/:submissionId" element={<PitchPage />} />
        </Routes>
      </main>
    </>
  );
}
