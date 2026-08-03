import { BASE_PATH } from '@/lib/utils'

export interface Screenshot {
  id: string
  src: string
  alt: string
}

export const screenshots: Screenshot[] = [
  {
    id: '1',
    src: `${BASE_PATH}/screenshots/Screenshot-1.png`,
    alt: 'PhoneSploit Pro main dashboard showing device connection and menu options',
  },
  {
    id: '2',
    src: `${BASE_PATH}/screenshots/Screenshot-2.png`,
    alt: 'PhoneSploit Pro device control panel with shell, screenshot, and recording options',
  },
  {
    id: '3',
    src: `${BASE_PATH}/screenshots/Screenshot-3.png`,
    alt: 'PhoneSploit Pro data extraction module showing file manager and data dump options',
  },
  {
    id: '4',
    src: `${BASE_PATH}/screenshots/Screenshot-4.png`,
    alt: 'PhoneSploit Pro media and app management interface',
  },
  {
    id: '5',
    src: `${BASE_PATH}/screenshots/Screenshot-5.png`,
    alt: 'PhoneSploit Pro exploitation module with Metasploit integration',
  },
]