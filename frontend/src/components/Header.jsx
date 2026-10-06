import React, { useEffect, useRef, useState } from "react";
import GoogleTranslate from "./GoogleTranslate";
import "../styles/Header.css";

function Header() {
  const [profileOpen, setProfileOpen] = useState(false);
  const [languageOpen, setLanguageOpen] = useState(false);

  const [selectedLanguage, setSelectedLanguage] = useState("English");

  const profileRef = useRef(null);
  const languageRef = useRef(null);

  // CLOSE DROPDOWNS WHEN CLICKING OUTSIDE

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileOpen(false);
      }

      if (languageRef.current && !languageRef.current.contains(event.target)) {
        setLanguageOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // ==========================================
  // GET CURRENT GOOGLE TRANSLATE LANGUAGE
  // ==========================================
  useEffect(() => {
    const cookies = document.cookie.split(";");

    const translateCookie = cookies.find((cookie) =>
      cookie.trim().startsWith("googtrans="),
    );

    if (translateCookie) {
      const value = translateCookie.split("=")[1]?.trim();

      if (value?.includes("/mr")) {
        setSelectedLanguage("मराठी");
      } else if (value?.includes("/hi")) {
        setSelectedLanguage("हिंदी");
      } else {
        setSelectedLanguage("English");
      }
    }
  }, []);

  // CHANGE LANGUAGE

  const changeLanguage = (language, languageName) => {
    setSelectedLanguage(languageName);
    setLanguageOpen(false);

    // ENGLISH
    if (language === "en") {
      // Remove Google Translate cookie
      document.cookie =
        "googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

      document.cookie = `googtrans=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; domain=${window.location.hostname};`;

      // Reload page
      window.location.reload();

      return;
    }

    // MARATHI / HINDI

    document.cookie = `googtrans=/en/${language}; path=/;`;

    document.cookie = `googtrans=/en/${language}; path=/; domain=${window.location.hostname};`;

    // Reload page to apply translation
    window.location.reload();
  };

  // LOGOUT
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");

    setProfileOpen(false);

    alert("You have been logged out.");

    // If you are using React Router:
    // navigate("/login");
  };

  return (
    <>
      {/*
          GOOGLE TRANSLATE
          Hidden from the user */}
      <GoogleTranslate />

      {/*HEADER */}
      <header className="header">
        {/*LOGO*/}
        <div className="header-logo">RBI SAATHI</div>

        {/*RIGHT SIDE*/}
        <div className="header-right">
          {/*LANGUAGE*/}
          <div className="language-container" ref={languageRef}>
            <button
              type="button"
              className="language-button"
              onClick={() => setLanguageOpen(!languageOpen)}
            >
              <span className="language-icon">🌐</span>

              <span className="language-name">{selectedLanguage}</span>

              <span className="dropdown-arrow">{languageOpen ? "▲" : "▼"}</span>
            </button>

            {/* LANGUAGE MENU */}
            {languageOpen && (
              <div className="language-dropdown">
                {/* English */}
                <button
                  type="button"
                  onClick={() => changeLanguage("en", "English")}
                >
                  <span>🇬🇧</span>
                  <span>English</span>
                </button>

                {/* Marathi */}
                <button
                  type="button"
                  onClick={() => changeLanguage("mr", "मराठी")}
                >
                  <span>🇮🇳</span>
                  <span>मराठी</span>
                </button>

                {/* Hindi */}
                <button
                  type="button"
                  onClick={() => changeLanguage("hi", "हिंदी")}
                >
                  <span>🇮🇳</span>
                  <span>हिंदी</span>
                </button>
              </div>
            )}
          </div>

          {/*NOTIFICATION*/}
          <button
            type="button"
            className="notification-button"
            title="Notifications"
          >
            🔔
            <span className="notification-dot"></span>
          </button>

          {/*PROFILE*/}
          <div className="profile-container" ref={profileRef}>
            {/* PROFILE BUTTON */}
            <button
              type="button"
              className="profile-button"
              onClick={() => setProfileOpen(!profileOpen)}
            >
              {/* Avatar */}
              <div className="profile-avatar">S</div>

              {/* Name and Role */}
              <div className="profile-info">
                <span className="profile-name">Siddhu</span>

                <span className="profile-role">Employee</span>
              </div>

              {/* Arrow */}
              <span className="dropdown-arrow">{profileOpen ? "▲" : "▼"}</span>
            </button>

            {/*PROFILE DROPDOWN*/}
            {profileOpen && (
              <div className="profile-dropdown">
                {/* PROFILE HEADER */}
                <div className="profile-dropdown-header">
                  <div className="profile-avatar large">S</div>

                  <div className="profile-dropdown-user">
                    <strong>Siddhu</strong>

                    <span>Employee</span>
                  </div>
                </div>

                {/* DIVIDER */}
                <div className="dropdown-divider"></div>

                {/* PROFILE */}
                <button
                  type="button"
                  className="dropdown-item"
                  onClick={() => setProfileOpen(false)}
                >
                  <span className="dropdown-item-icon">👤</span>

                  <span>Profile</span>
                </button>

                {/* SETTINGS */}
                <button
                  type="button"
                  className="dropdown-item"
                  onClick={() => setProfileOpen(false)}
                >
                  <span className="dropdown-item-icon">⚙️</span>

                  <span>Settings</span>
                </button>

                {/* DIVIDER */}
                <div className="dropdown-divider"></div>

                {/* LOGOUT */}
                <button
                  type="button"
                  className="dropdown-item logout-item"
                  onClick={handleLogout}
                >
                  <span className="dropdown-item-icon">🚪</span>

                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </header>
    </>
  );
}

export default Header;
