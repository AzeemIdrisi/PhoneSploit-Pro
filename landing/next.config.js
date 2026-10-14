const fs = require('fs')
const path = require('path')

const versionPath = path.join(__dirname, '..', 'VERSION')
let appVersion = ''
if (fs.existsSync(versionPath)) {
  appVersion = fs.readFileSync(versionPath, 'utf8').trim()
}
if (!appVersion) {
  throw new Error(`Missing or empty VERSION file at ${versionPath}`)
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
