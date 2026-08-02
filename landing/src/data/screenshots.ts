import { BASE_PATH } from '@/lib/utils'

export interface Screenshot {
  id: string
  src: string
  alt: string
  caption: string
  width: number
  height: number
}

export const screenshots: Screenshot[] = [
  {
    id: '1',
    src: `${BASE_PATH}/screenshots/Screenshot-1.png`,
    alt: 'PhoneSploit Pro main dashboard showing device connection and menu options',
    caption: 'Main Dashboard — Device connection and feature navigation',
    width: 1200,
    height: 800,
  },
  {
    id: '2',
    src: `${BASE_PATH}/screenshots/Screenshot-2.png`,
    alt: 'PhoneSploit Pro device control panel with shell, screenshot, and recording options',
    caption: 'Device Control — Shell, screen capture, and remote control',
    width: 1200,
    height: 800,
  },
  {
    id: '3',
    src: `${BASE_PATH}/screenshots/Screenshot-3.png`,
    alt: 'PhoneSploit Pro data extraction module showing file manager and data dump options',
    caption: 'Data Extraction — File manager, SMS, contacts, call logs',
    width: 1200,
    height: 800,
  },
  {
    id: '4',
    src: `${BASE_PATH}/screenshots/Screenshot-4.png`,
    alt: 'PhoneSploit Pro media and app management interface',
    caption: 'Media & Apps — Camera, microphone, app install/uninstall',
    width: 1200,
    height: 800,
  },
  {
    id: '5',
    src: `${BASE_PATH}/screenshots/Screenshot-5.png`,
    alt: 'PhoneSploit Pro exploitation module with Metasploit integration',
    caption: 'Exploitation — Automated Metasploit payload delivery and Meterpreter session',
    width: 1200,
    height: 800,
  },
]