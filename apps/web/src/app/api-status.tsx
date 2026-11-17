"use client";

import { useEffect, useState } from "react";

type Health = { status: string; environment: string; database: string };

type State =
  | { kind: "loading" }
  | { kind: "ok"; health: Health }
  | { kind: "error"; message: string };

export function ApiStatus() {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    fetch("/api/health")
      .then(async (res) => {
        if (!res.ok) throw new Error(`API returned ${res.status}`);
        setState({ kind: "ok", health: (await res.json()) as Health });
      })
      .catch((err: unknown) =>
        setState({
          kind: "error",
          message: err instanceof Error ? err.message : "Could not reach the API",
        }),
      );
  }, []);

  if (state.kind === "loading") {
    return <p className="rounded-lg border p-4">Checking API…</p>;
  }
  if (state.kind === "error") {
    return (
      <p className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-800 dark:border-red-800 dark:bg-red-950 dark:text-red-200">
        API unreachable: {state.message}. Is the backend running on port 8000?
      </p>
    );
  }
  return (
    <p className="rounded-lg border border-green-300 bg-green-50 p-4 text-green-800 dark:border-green-800 dark:bg-green-950 dark:text-green-200">
      API OK · environment: {state.health.environment} · database:{" "}
      {state.health.database}
    </p>
  );
}
