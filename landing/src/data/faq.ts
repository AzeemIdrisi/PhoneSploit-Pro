export type FaqItem = {
  id: string;
  question: string;
  answer: string;
};

export const faqItems: FaqItem[] = [
  {
    id: "free",
    question: "Is PhoneSploit Pro free to use?",
    answer:
      "Yes. PhoneSploit Pro is open source under GPL-3.0. You can clone, use, and modify it according to the license terms.",
  },
  {
    id: "root",
    question: "Does it require root on the target device?",
    answer:
      "Most features work over ADB without root on the target. Some operations depend on what the device allows via USB debugging and Android version. Root on the attacker machine is not required for typical use.",
  },
  {
    id: "connection",
    question: "USB or Wi-Fi — which should I use?",
    answer:
      "USB is the most reliable for first setup. Wi-Fi ADB works once the device is paired or authorized on the same network. PhoneSploit Pro supports listing and selecting multiple connected devices.",
  },
  {
    id: "windows",
    question: "How well does Windows work?",
    answer:
      "Windows 11 is supported but experimental. scrcpy integration, some ADB workflows, and Metasploit automation may need extra setup. Linux or macOS is recommended for full feature parity.",
  },
  {
    id: "legal",
    question: "Is this legal to use?",
    answer:
      "Only on devices and networks you own or have explicit written permission to test. PhoneSploit Pro is intended for authorized security research and education. Unauthorized access is illegal.",
  },
  {
    id: "install",
    question: "How do I install it?",
    answer:
      "Clone the repository, create a Python 3.10+ virtual environment, run pip install -r requirements.txt, then python3 phonesploitpro.py. Optional install.sh or install.ps1 scripts help install ADB, scrcpy, Nmap, and Metasploit.",
  },
  {
    id: "python",
    question: "Which Python version do I need?",
    answer: "Python 3.10 or newer. Termux, Linux, macOS, and Windows are all documented in the Install section.",
  },
];
