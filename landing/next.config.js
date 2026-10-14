const fs = require('fs')
const path = require('path')

function readVersionFile(filePath) {
  if (!fs.existsSync(filePath)) return ''
  return fs.readFileSync(filePath, 'utf8').trim()
}

// Repo-root VERSION is canonical for local builds and GitHub Pages.
// landing/VERSION is the copy Vercel can see when Root Directory is `landing`.
const repoVersionPath = path.join(__dirname, '..', 'VERSION')
const landingVersionPath = path.join(__dirname, 'VERSION')
const repoVersion = readVersionFile(repoVersionPath)
const landingVersion = readVersionFile(landingVersionPath)

if (repoVersion && landingVersion && repoVersion !== landingVersion) {
  throw new Error(
    `VERSION mismatch: ${landingVersionPath} is "${landingVersion}" but ${repoVersionPath} is "${repoVersion}"`,
  )
}

const appVersion = repoVersion || landingVersion
if (!appVersion) {
  throw new Error(
    `Missing or empty VERSION file. Checked ${repoVersionPath} and ${landingVersionPath}`,
  )
}

const isGitHubPages = process.env.GITHUB_PAGES === '1'

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_APP_VERSION: appVersion,
  },
  ...(isGitHubPages && {
    output: 'export',
    basePath: '/PhoneSploit-Pro',
    assetPrefix: '/PhoneSploit-Pro/',
  }),
  images: { unoptimized: true },
  trailingSlash: true,
}

module.exports = nextConfig
