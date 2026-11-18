import { useEffect, useState } from "react";

interface Props {
  remaining: number;
  planned: number;
  onExpire: () => void;
}

export default function Timer({ remaining, planned, onExpire }: Props) {
  const [left, setLeft] = useState(remaining);

  useEffect(() => {
    setLeft(remaining);
  }, [remaining]);

  useEffect(() => {
    if (left <= 0) {
      onExpire();
      return;
    }
    const id = window.setTimeout(() => setLeft((s) => s - 1), 1000);
    return () => window.clearTimeout(id);
  }, [left, onExpire]);

  const minutes = Math.floor(left / 60);
  const seconds = String(left % 60).padStart(2, "0");
  const warning = left <= 60;

  return (
    <div className={`timer ${warning ? "warning" : ""}`}>
      <span>
        {minutes}:{seconds}
      </span>
      <progress value={planned - left} max={planned} />
    </div>
  );
}
