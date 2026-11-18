import { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import type { PitchState } from "../api/types";
import Timer from "../components/Timer";

const STAGE_LABELS: Record<string, string> = {
  pitch: "Питч: расскажите о проекте без перебиваний",
  qa: "Вопросы инвестора",
  feedback: "Обратная связь",
};

export default function PitchPage() {
  const { submissionId } = useParams();
  const [state, setState] = useState<PitchState | null>(null);
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);

  const start = async () => {
    if (!submissionId) return;
    setBusy(true);
    const session = await api.createPitch(submissionId);
    setState(await api.pitchNext(session.id));
    setBusy(false);
  };

  const sync = useCallback(async () => {
    if (state) setState(await api.pitch(state.id));
  }, [state?.id]);

  const next = async () => {
    if (!state) return;
    setBusy(true);
    setState(await api.pitchNext(state.id));
    setBusy(false);
  };

  const send = async () => {
    if (!state || !answer.trim()) return;
    setState(await api.pitchMessage(state.id, answer.trim()));
    setAnswer("");
  };

  if (!state) {
    return (
      <section>
        <h1>Тренировка питча с инвестором-ментором</h1>
        <p>Регламент: питч 5 минут без перебиваний → вопросы 2–3 минуты → обратная связь. Время контролирует приложение.</p>
        <button disabled={busy} onClick={start}>
          Начать
        </button>
      </section>
    );
  }

  if (state.status === "finished") {
    return (
      <section>
        <h1>Сессия завершена</h1>
        <table>
          <thead>
            <tr>
              <th>Этап</th>
              <th>План, сек</th>
              <th>Факт, сек</th>
            </tr>
          </thead>
          <tbody>
            {state.stages.map((s) => (
              <tr key={s.stage}>
                <td>{STAGE_LABELS[s.stage] ?? s.stage}</td>
                <td>{s.planned_sec}</td>
                <td>{s.actual_sec ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    );
  }

  return (
    <section>
      <h1>{STAGE_LABELS[state.stage ?? ""]}</h1>
      {state.remaining_sec !== null && state.planned_sec !== null && (
        <Timer key={state.stage} remaining={state.remaining_sec} planned={state.planned_sec} onExpire={sync} />
      )}
      {state.stage === "pitch" && <p className="muted">Инвестор слушает. Когда закончите раньше времени, нажмите «Завершить этап».</p>}
      {state.stage === "qa" && (
        <>
          <ol>
            {state.questions.map((q) => (
              <li key={q}>{q}</li>
            ))}
          </ol>
          <textarea value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Ваш ответ (в MVP — текстом)" />
          <button onClick={send}>Отправить ответ</button>
        </>
      )}
      {state.stage === "feedback" && (
        <div className="card">
          <h2>Сильные стороны</h2>
          <ul>{state.feedback.strengths?.map((s) => <li key={s}>{s}</li>)}</ul>
          <h2>Замечания</h2>
          <ul>{state.feedback.remarks?.map((r) => <li key={r}>{r}</li>)}</ul>
        </div>
      )}
      <button className="secondary" disabled={busy} onClick={next}>
        Завершить этап
      </button>
    </section>
  );
}
