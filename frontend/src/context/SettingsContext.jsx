import React, { createContext, useContext, useEffect, useState } from "react";

const SettingsContext = createContext();

const normalizeLanguage = (value) => {
  const normalized = String(value || "").trim().toLowerCase();
  if (normalized === "hi" || normalized === "hindi") return "Hindi";
  if (normalized === "mr" || normalized === "marathi") return "Marathi";
  return "English";
};

const languageCode = (value) =>
  normalizeLanguage(value) === "Hindi"
    ? "hi"
    : normalizeLanguage(value) === "Marathi"
      ? "mr"
      : "en";

const applyTranslationLanguage = (value) => {
  const code = languageCode(value);
  if (code === "en") {
    document.cookie =
      "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie =
      `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname};`;
  } else {
    document.cookie = `googtrans=/en/${code}; path=/;`;
    document.cookie =
      `googtrans=/en/${code}; path=/; domain=${window.location.hostname};`;
  }
};

export const SettingsProvider = ({ children }) => {
  const [languageState, setLanguageState] = useState(() =>
    normalizeLanguage(localStorage.getItem("language")),
  );

  const setLanguage = (value) => {
    const nextLanguage = normalizeLanguage(value);
    if (nextLanguage === languageState) return;

    setLanguageState(nextLanguage);
    localStorage.setItem("language", nextLanguage);
    document.documentElement.setAttribute("lang", languageCode(nextLanguage));
    applyTranslationLanguage(nextLanguage);

    // Google Translate reads the googtrans cookie during page initialization.
    // Reload only after an explicit user selection so the choice is applied.
    window.location.reload();
  };

  const [appearance, setAppearance] = useState(
    localStorage.getItem("appearance") || "Light",
  );

  const [notifications, setNotifications] = useState({
    learning: true,
    assessments: true,
    updates: false,
  });

  const [preferences, setPreferences] = useState({
    reminders: true,
    progress: true,
  });

  useEffect(() => {
    localStorage.setItem("language", languageState);
    document.documentElement.setAttribute("lang", languageCode(languageState));
  }, [languageState]);

  useEffect(() => {
    localStorage.setItem("appearance", appearance);

    let theme = appearance;

    if (appearance === "System Default") {
      theme = window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "Dark"
        : "Light";
    }

    document.documentElement.setAttribute("data-theme", theme.toLowerCase());
  }, [appearance]);

  return (
    <SettingsContext.Provider
      value={{
        language: languageState,
        setLanguage,
        appearance,
        setAppearance,
        notifications,
        setNotifications,
        preferences,
        setPreferences,
      }}
    >
      {children}
    </SettingsContext.Provider>
  );
};

export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error("useSettings must be used inside SettingsProvider");
  }
  return context;
};
