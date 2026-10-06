import React, { createContext, useContext, useState } from "react";

const LanguageContext = createContext();

const translations = {
  // =====================================================
  // ENGLISH
  // =====================================================
  en: {
    // Header
    appName: "RBI SAATHI",
    employee: "Employee",
    profile: "Profile",
    settings: "Settings",
    logout: "Logout",
    english: "English",
    marathi: "मराठी",
    hindi: "हिंदी",
    notifications: "Notifications",

    // Sidebar
    dashboard: "Dashboard",
    updates: "Updates",
    learning: "Learning",
    myLearning: "My Learning",
    assessments: "Assessments",
    askSaathi: "Ask Saathi",
    progress: "Progress",
    courses: "Courses",
    reports: "Reports",
    help: "Help & Support",

    // Greeting
    goodMorning: "Good Morning",
    goodAfternoon: "Good Afternoon",
    goodEvening: "Good Evening",
    welcomeBack: "Welcome back to",

    // Statistics
    learningStat: "Learning",
    completed: "Completed",
    pending: "Pending",
    progressStat: "Progress",

    // Dashboard sections
    upcomingAssessments: "Upcoming Assessments",
    recommended: "Recommended For You",
    viewAll: "View All",

    // Continue Learning
    continueLearning: "Continue Learning",
    resume: "Resume",
    viewCourse: "View Course",
    lessons: "Lessons",
    completedText: "completed",

    // Recent Updates
    recentUpdates: "Recent Updates",
    newCourse: "New course available",
    assessmentDue: "Assessment is due soon",
    systemUpdate: "System update completed",
    today: "Today",
    yesterday: "Yesterday",

    // Assessment
    assessment: "Assessment",
    startAssessment: "Start Assessment",
    questions: "Questions",
    duration: "Duration",
    minutes: "minutes",

    // Courses
    banking: "Banking",
    professionalSkills: "Professional Skills",
    compliance: "Compliance",
    hours: "hours",
    hour: "hour",

    // Course names
    digitalBanking: "Digital Banking & Security",
    customerService: "Customer Service Excellence",
    rbiGuidelines: "RBI Guidelines & Compliance",

    // Logout
    logoutMessage: "You have been logged out.",
  },

  // =====================================================
  // MARATHI
  // =====================================================
  mr: {
    // Header
    appName: "RBI SAATHI",
    employee: "कर्मचारी",
    profile: "प्रोफाइल",
    settings: "सेटिंग्ज",
    logout: "लॉग आउट",
    english: "English",
    marathi: "मराठी",
    hindi: "हिंदी",
    notifications: "सूचना",

    // Sidebar
    dashboard: "डॅशबोर्ड",
    updates: "अपडेट्स",
    learning: "शिक्षण",
    myLearning: "माझे शिक्षण",
    assessments: "मूल्यांकन",
    askSaathi: "साथीला विचारा",
    progress: "प्रगती",
    courses: "अभ्यासक्रम",
    reports: "अहवाल",
    help: "मदत आणि सहाय्य",

    // Greeting
    goodMorning: "शुभ सकाळ",
    goodAfternoon: "शुभ दुपार",
    goodEvening: "शुभ संध्याकाळ",
    welcomeBack: "पुन्हा स्वागत आहे",

    // Statistics
    learningStat: "शिक्षण",
    completed: "पूर्ण",
    pending: "प्रलंबित",
    progressStat: "प्रगती",

    // Dashboard sections
    upcomingAssessments: "आगामी मूल्यांकन",
    recommended: "तुमच्यासाठी शिफारस केलेले",
    viewAll: "सर्व पहा",

    // Continue Learning
    continueLearning: "शिक्षण सुरू ठेवा",
    resume: "पुन्हा सुरू करा",
    viewCourse: "अभ्यासक्रम पहा",
    lessons: "धडे",
    completedText: "पूर्ण",

    // Recent Updates
    recentUpdates: "अलीकडील अपडेट्स",
    newCourse: "नवीन अभ्यासक्रम उपलब्ध आहे",
    assessmentDue: "मूल्यांकनाची अंतिम वेळ जवळ आली आहे",
    systemUpdate: "सिस्टम अपडेट पूर्ण झाले",
    today: "आज",
    yesterday: "काल",

    // Assessment
    assessment: "मूल्यांकन",
    startAssessment: "मूल्यांकन सुरू करा",
    questions: "प्रश्न",
    duration: "कालावधी",
    minutes: "मिनिटे",

    // Courses
    banking: "बँकिंग",
    professionalSkills: "व्यावसायिक कौशल्ये",
    compliance: "अनुपालन",
    hours: "तास",
    hour: "तास",

    // Course names
    digitalBanking: "डिजिटल बँकिंग आणि सुरक्षा",
    customerService: "ग्राहक सेवा उत्कृष्टता",
    rbiGuidelines: "RBI मार्गदर्शक तत्त्वे आणि अनुपालन",

    // Logout
    logoutMessage: "तुम्ही लॉग आउट केले आहे.",
  },

  // =====================================================
  // HINDI
  // =====================================================
  hi: {
    // Header
    appName: "RBI SAATHI",
    employee: "कर्मचारी",
    profile: "प्रोफ़ाइल",
    settings: "सेटिंग्स",
    logout: "लॉग आउट",
    english: "English",
    marathi: "मराठी",
    hindi: "हिंदी",
    notifications: "सूचनाएं",

    // Sidebar
    dashboard: "डैशबोर्ड",
    updates: "अपडेट्स",
    learning: "सीखना",
    myLearning: "मेरी सीख",
    assessments: "मूल्यांकन",
    askSaathi: "साथी से पूछें",
    progress: "प्रगति",
    courses: "पाठ्यक्रम",
    reports: "रिपोर्ट",
    help: "मदद और सहायता",

    // Greeting
    goodMorning: "सुप्रभात",
    goodAfternoon: "नमस्कार",
    goodEvening: "शुभ संध्या",
    welcomeBack: "आपका फिर से स्वागत है",

    // Statistics
    learningStat: "सीखना",
    completed: "पूर्ण",
    pending: "लंबित",
    progressStat: "प्रगति",

    // Dashboard sections
    upcomingAssessments: "आगामी मूल्यांकन",
    recommended: "आपके लिए अनुशंसित",
    viewAll: "सभी देखें",

    // Continue Learning
    continueLearning: "सीखना जारी रखें",
    resume: "फिर से शुरू करें",
    viewCourse: "पाठ्यक्रम देखें",
    lessons: "पाठ",
    completedText: "पूर्ण",

    // Recent Updates
    recentUpdates: "हाल के अपडेट्स",
    newCourse: "नया पाठ्यक्रम उपलब्ध है",
    assessmentDue: "मूल्यांकन की अंतिम तिथि जल्द है",
    systemUpdate: "सिस्टम अपडेट पूरा हुआ",
    today: "आज",
    yesterday: "कल",

    // Assessment
    assessment: "मूल्यांकन",
    startAssessment: "मूल्यांकन शुरू करें",
    questions: "प्रश्न",
    duration: "अवधि",
    minutes: "मिनट",

    // Courses
    banking: "बैंकिंग",
    professionalSkills: "व्यावसायिक कौशल",
    compliance: "अनुपालन",
    hours: "घंटे",
    hour: "घंटा",

    // Course names
    digitalBanking: "डिजिटल बैंकिंग और सुरक्षा",
    customerService: "ग्राहक सेवा उत्कृष्टता",
    rbiGuidelines: "RBI दिशानिर्देश और अनुपालन",

    // Logout
    logoutMessage: "आप लॉग आउट हो चुके हैं।",
  },
};

// =====================================================
// LANGUAGE PROVIDER
// =====================================================

export const LanguageProvider = ({ children }) => {
  const [language, setLanguageState] = useState(
    localStorage.getItem("language") || "en",
  );

  const setLanguage = (lang) => {
    setLanguageState(lang);
    localStorage.setItem("language", lang);
  };

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        t: translations[language],
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};

// =====================================================
// CUSTOM HOOK
// =====================================================

export const useLanguage = () => {
  const context = useContext(LanguageContext);

  if (!context) {
    throw new Error("useLanguage must be used inside LanguageProvider");
  }

  return context;
};
