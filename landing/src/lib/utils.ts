import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

const GITHUB_PAGES_BASE_PATH = '/PhoneSploit-Pro'
const GITHUB_PAGES_SITE_URL = 'https://azeemidrisi.github.io/PhoneSploit-Pro'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getBasePath(): string {
  if (process.env.NEXT_PUBLIC_BASE_PATH !== undefined) {
    return process.env.NEXT_PUBLIC_BASE_PATH
  }
  if (process.env.GITHUB_PAGES === '1') {
    return GITHUB_PAGES_BASE_PATH
  }
  return ''
}

export function getSiteUrl(): string {
  if (process.env.NEXT_PUBLIC_SITE_URL) {
    return process.env.NEXT_PUBLIC_SITE_URL.replace(/\/?$/, '/')
  }
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}/`
  }
  return `${GITHUB_PAGES_SITE_URL}/`
}
