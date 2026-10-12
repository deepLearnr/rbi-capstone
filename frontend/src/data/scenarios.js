export const SCENARIO_CATEGORIES = [
  {
    id: "cyber-security",
    title: "Cyber Security",
    category: "CYBER SECURITY",
    icon: "🔐",
    description:
      "Practice responses to suspicious emails, unknown devices, and password-sharing requests.",
    questions: [
      {
        title: "Suspicious Email",
        situation:
          "You receive an email that appears to come from an official source. The email asks you to click a link and provide confidential information.",
        question: "What should you do?",
        options: [
          "Click the link and verify the information",
          "Share the requested information",
          "Follow the organization's security procedure and report the suspicious email through the appropriate channel",
          "Forward the email to colleagues",
        ],
        correctAnswer: 2,
        explanation:
          "Follow the organization's approved security procedure when handling suspicious communications.",
        learning: "Cyber Security → Phishing Awareness",
      },
      {
        title: "Unknown USB Device",
        situation:
          "You find an unknown USB device near your workstation. You are unsure who owns it.",
        question: "What should you do?",
        options: [
          "Connect it to your computer to identify the owner",
          "Give it to a colleague to check",
          "Report it through the organization's security procedure",
          "Use it only on a personal computer",
        ],
        correctAnswer: 2,
        explanation:
          "Unknown devices should not be connected to organizational systems. Report them through the approved security process.",
        learning: "Cyber Security → Device Security",
      },
      {
        title: "Password Security",
        situation:
          "A colleague asks you to share your system password because they need quick access to complete a task.",
        question: "What should you do?",
        options: [
          "Share your password because the colleague is trusted",
          "Write the password on a note",
          "Refuse to share it and follow the approved access process",
          "Send the password through email",
        ],
        correctAnswer: 2,
        explanation:
          "Passwords must remain confidential. Access should be provided through the organization's approved access process.",
        learning: "Cyber Security → Password & Access Security",
      },
    ],
  },
  {
    id: "compliance",
    title: "Compliance",
    category: "COMPLIANCE",
    icon: "📋",
    description:
      "Practice handling requests for customer information and checking authorization.",
    questions: [
      {
        title: "Customer Information",
        situation:
          "A person outside your team asks you to send customer information for an unofficial purpose.",
        question: "What should you do?",
        options: [
          "Send the information immediately",
          "Share only some of the information",
          "Verify authorization and follow the approved data-sharing procedure",
          "Forward the request to another employee",
        ],
        correctAnswer: 2,
        explanation:
          "Customer information should only be shared with authorized people through approved procedures.",
        learning: "Compliance → Data Protection",
      },
    ],
  },
  {
    id: "risk",
    title: "Risk & Fraud",
    category: "RISK",
    icon: "⚠️",
    description:
      "Practice responding to unusual transaction activity through internal processes.",
    questions: [
      {
        title: "Unusual Transaction",
        situation:
          "You notice an unusual transaction that does not match the normal pattern of activity.",
        question: "What should you do?",
        options: [
          "Ignore it because it may be normal",
          "Discuss it with friends",
          "Report it through the appropriate internal process",
          "Delete the transaction record",
        ],
        correctAnswer: 2,
        explanation:
          "Unusual activity should be reported through the organization's approved risk and fraud reporting process.",
        learning: "Risk Management → Fraud Awareness",
      },
    ],
  },
];

export function getScenarioCategory(id) {
  return SCENARIO_CATEGORIES.find((scenario) => scenario.id === id) ?? null;
}
