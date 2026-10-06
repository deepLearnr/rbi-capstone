import React, { useState } from "react";
import "../styles/Settings.css";

import { useSettings } from "../context/SettingsContext";

function Settings() {
  const [activeSetting, setActiveSetting] = useState("language");
  const [saved, setSaved] = useState(false);

  const {
    language,
    setLanguage,

    appearance,
    setAppearance,

    notifications,
    setNotifications,

    preferences,
    setPreferences,
  } = useSettings();

  const settingsMenu = [
    {
      id: "language",
      icon: "🌐",
      label: "Language",
    },
    {
      id: "notifications",
      icon: "🔔",
      label: "Notifications",
    },
    {
      id: "appearance",
      icon: "🎨",
      label: "Appearance",
    },
    {
      id: "security",
      icon: "🔐",
      label: "Account & Security",
    },
    {
      id: "preferences",
      icon: "🔊",
      label: "Preferences",
    },
  ];

  const handleSave = () => {
    setSaved(true);

    setTimeout(() => {
      setSaved(false);
    }, 2500);
  };

  const renderContent = () => {
    switch (activeSetting) {
      /* ================= LANGUAGE ================= */

      case "language":
        return (
          <>
            <div className="settings-content-header">
              <h2>Language</h2>
              <p>Select your preferred language</p>
            </div>

            <div className="language-options">
              <label className="radio-option">
                <input
                  type="radio"
                  name="language"
                  value="English"
                  checked={language === "English"}
                  onChange={(e) => setLanguage(e.target.value)}
                />

                <span>English</span>
              </label>

              <label className="radio-option">
                <input
                  type="radio"
                  name="language"
                  value="Hindi"
                  checked={language === "Hindi"}
                  onChange={(e) => setLanguage(e.target.value)}
                />

                <span>Hindi</span>
              </label>

              <label className="radio-option">
                <input
                  type="radio"
                  name="language"
                  value="Marathi"
                  checked={language === "Marathi"}
                  onChange={(e) => setLanguage(e.target.value)}
                />

                <span>Marathi</span>
              </label>
            </div>
          </>
        );

      /* ================= NOTIFICATIONS ================= */

      case "notifications":
        return (
          <>
            <div className="settings-content-header">
              <h2>Notifications</h2>
              <p>Manage your notification preferences</p>
            </div>

            <div className="settings-options">
              <label className="toggle-option">
                <div>
                  <strong>Learning Reminders</strong>
                  <p>Receive reminders about your learning activities.</p>
                </div>

                <input
                  type="checkbox"
                  checked={notifications.learning}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      learning: e.target.checked,
                    })
                  }
                />
              </label>

              <label className="toggle-option">
                <div>
                  <strong>Assessment Notifications</strong>
                  <p>Get notified about upcoming assessments.</p>
                </div>

                <input
                  type="checkbox"
                  checked={notifications.assessments}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      assessments: e.target.checked,
                    })
                  }
                />
              </label>

              <label className="toggle-option">
                <div>
                  <strong>Regulatory Updates</strong>
                  <p>Receive notifications about important updates.</p>
                </div>

                <input
                  type="checkbox"
                  checked={notifications.updates}
                  onChange={(e) =>
                    setNotifications({
                      ...notifications,
                      updates: e.target.checked,
                    })
                  }
                />
              </label>
            </div>
          </>
        );

      /* ================= APPEARANCE ================= */

      case "appearance":
        return (
          <>
            <div className="settings-content-header">
              <h2>Appearance</h2>
              <p>Choose how the application looks.</p>
            </div>

            <div className="appearance-options">
              <label className="radio-option">
                <input
                  type="radio"
                  name="appearance"
                  value="Light"
                  checked={appearance === "Light"}
                  onChange={(e) => setAppearance(e.target.value)}
                />

                <span>☀️ Light</span>
              </label>

              <label className="radio-option">
                <input
                  type="radio"
                  name="appearance"
                  value="Dark"
                  checked={appearance === "Dark"}
                  onChange={(e) => setAppearance(e.target.value)}
                />

                <span>🌙 Dark</span>
              </label>

              <label className="radio-option">
                <input
                  type="radio"
                  name="appearance"
                  value="System Default"
                  checked={appearance === "System Default"}
                  onChange={(e) => setAppearance(e.target.value)}
                />

                <span>💻 System Default</span>
              </label>
            </div>
          </>
        );

      /* ================= SECURITY ================= */

      case "security":
        return (
          <>
            <div className="settings-content-header">
              <h2>Account & Security</h2>
              <p>Manage your account security settings.</p>
            </div>

            <div className="security-options">
              <div className="security-item">
                <div>
                  <strong>Change Password</strong>
                  <p>Update your account password.</p>
                </div>

                <button
                  onClick={() => alert("Change password option selected.")}
                >
                  Change
                </button>
              </div>

              <div className="security-item">
                <div>
                  <strong>Two-Factor Authentication</strong>
                  <p>Add an extra layer of account security.</p>
                </div>

                <button
                  onClick={() => alert("Two-factor authentication selected.")}
                >
                  Manage
                </button>
              </div>

              <div className="security-item">
                <div>
                  <strong>Active Sessions</strong>
                  <p>Review devices currently signed in.</p>
                </div>

                <button onClick={() => alert("Active sessions selected.")}>
                  View
                </button>
              </div>
            </div>
          </>
        );

      /* ================= PREFERENCES ================= */

      case "preferences":
        return (
          <>
            <div className="settings-content-header">
              <h2>Preferences</h2>
              <p>Manage your learning and application preferences.</p>
            </div>

            <div className="settings-options">
              <label className="toggle-option">
                <div>
                  <strong>Learning Reminders</strong>
                  <p>Remind me to continue unfinished courses.</p>
                </div>

                <input
                  type="checkbox"
                  checked={preferences.reminders}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      reminders: e.target.checked,
                    })
                  }
                />
              </label>

              <label className="toggle-option">
                <div>
                  <strong>Progress Tracking</strong>
                  <p>Track learning progress and performance.</p>
                </div>

                <input
                  type="checkbox"
                  checked={preferences.progress}
                  onChange={(e) =>
                    setPreferences({
                      ...preferences,
                      progress: e.target.checked,
                    })
                  }
                />
              </label>
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <div className="settings-page">
      {/* ================= HEADER ================= */}

      <div className="settings-header">
        <h1>Settings</h1>

        <p>Manage your account, preferences and notifications</p>
      </div>

      {/* ================= SETTINGS BODY ================= */}

      <div className="settings-container">
        {/* LEFT MENU */}

        <aside className="settings-menu">
          <h3>SETTINGS MENU</h3>

          {settingsMenu.map((item) => (
            <button
              key={item.id}
              className={`settings-menu-item ${
                activeSetting === item.id ? "active" : ""
              }`}
              onClick={() => setActiveSetting(item.id)}
            >
              <span className="settings-menu-icon">{item.icon}</span>

              <span>{item.label}</span>
            </button>
          ))}
        </aside>

        {/* RIGHT CONTENT */}

        <main className="settings-content">
          {renderContent()}

          <div className="settings-save-area">
            <button className="save-settings-button" onClick={handleSave}>
              Save Changes
            </button>

            {saved && (
              <span className="settings-saved-message">
                ✓ Changes saved successfully
              </span>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default Settings;
