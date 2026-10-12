const ATTEMPTS_KEY = "rbi-saathi-scenario-attempts-v1";
const SESSION_PREFIX = "rbi-saathi-scenario-session-v2:";

// Generate attempt IDs outside React render code so the component remains pure.
export function createScenarioAttemptId(scenarioId) {
  const uniqueId =
    typeof globalThis.crypto?.randomUUID === "function"
      ? globalThis.crypto.randomUUID()
      : `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  return `${scenarioId}-${uniqueId}`;
}

function readJson(key, fallback) {
  if (typeof window === "undefined") return fallback;
  try {
    const value = window.localStorage.getItem(key);
    return value ? JSON.parse(value) : fallback;
  } catch {
    return fallback;
  }
}

function writeJson(key, value) {
  if (typeof window === "undefined") return false;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    return true;
  } catch {
    // Private browsing or storage quota can disable persistence. The quiz remains usable.
    return false;
  }
}

export function getScenarioAttempts() {
  const attempts = readJson(ATTEMPTS_KEY, []);
  return Array.isArray(attempts) ? attempts : [];
}

export function saveScenarioAttempt(attempt) {
  const attempts = getScenarioAttempts();
  if (attempts.some((existing) => existing.id === attempt.id)) {
    return attempts;
  }
  const next = [attempt, ...attempts].slice(0, 100);
  writeJson(ATTEMPTS_KEY, next);
  return next;
}

export function getScenarioSession(scenarioId) {
  if (typeof window === "undefined") return null;
  const session = readJson(`${SESSION_PREFIX}${scenarioId}`, null);
  return session && typeof session === "object" ? session : null;
}

export function saveScenarioSession(scenarioId, session) {
  if (typeof window === "undefined") return false;
  return writeJson(`${SESSION_PREFIX}${scenarioId}`, session);
}

export function getScenarioPerformance() {
  const attempts = getScenarioAttempts();
  if (attempts.length === 0) {
    return { attempts: 0, averageScore: null, completedScenarios: 0 };
  }
  const totalPercent = attempts.reduce(
    (sum, attempt) => sum + (Number(attempt.scorePercent) || 0),
    0,
  );
  return {
    attempts: attempts.length,
    averageScore: Math.round(totalPercent / attempts.length),
    completedScenarios: new Set(attempts.map((attempt) => String(attempt.scenarioId))).size,
  };
}
