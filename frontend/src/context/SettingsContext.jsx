import React, { createContext, useContext, useEffect, useState } from "react";

const SettingsContext = createContext();

export const SettingsProvider = ({ children }) => {
  const [language, setLanguage] = useState(
    localStorage.getItem("language") || "English",
  );

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

  // ================= LANGUAGE =================
  useEffect(() => {
    localStorage.setItem("language", language);

    document.documentElement.setAttribute(
      "lang",
      language === "Hindi" ? "hi" : language === "Marathi" ? "mr" : "en",
    );
  }, [language]);

  // ================= APPEARANCE =================
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
        language,
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
  return useContext(SettingsContext);
};
