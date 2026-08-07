const isGitHubPages = process.env.GITHUB_PAGES === '1'

/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(isGitHubPages && {
    output: 'export',
    basePath: '/PhoneSploit-Pro',
    assetPrefix: '/PhoneSploit-Pro/',
  }),
  images: { unoptimized: true },
  trailingSlash: true,
}

module.exports = nextConfig
