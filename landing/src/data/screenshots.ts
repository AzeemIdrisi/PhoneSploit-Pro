import { getBasePath } from "@/lib/utils";

const basePath = getBasePath();

export interface Screenshot {
  id: string;
  src: string;
  alt: string;
}

export const screenshots: Screenshot[] = [
  {
    id: "1",
    src: `${basePath}/screenshots/Screenshot-1.png`,
    alt: "PhoneSploit Pro main dashboard showing device connection and menu options",
  },
];
