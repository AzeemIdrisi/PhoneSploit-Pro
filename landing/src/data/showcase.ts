export interface ShowcaseVideo {
  id: string;
  title: string;
  videoId: string;
  start?: number;
}

export const showcaseVideos: ShowcaseVideo[] = [
  {
    id: "demo-1",
    title: "PhoneSploit Pro — Device Exploitation Demo",
    videoId: "nPcq7zsgeKw",
  },
  {
    id: "demo-2",
    title: "PhoneSploit Pro — Control & Data Extraction Demo",
    videoId: "R46HFvBMtJM",
  },
  {
    id: "demo-3",
    title: "PhoneSploit Pro — Overview",
    videoId: "xDfHKB3NdTg",
  },
];
