const fs = require('fs');
const path = require('path');

const GITHUB_REPO = 'AzeemIdrisi/PhoneSploit-Pro';
const GITHUB_API = `https://api.github.com/repos/${GITHUB_REPO}`;

async function fetchGitHubStats() {
  try {
    console.log('Fetching GitHub stats...');
    
    const headers = {};
    if (process.env.GITHUB_TOKEN) {
      headers.Authorization = `token ${process.env.GITHUB_TOKEN}`;
    }

    const response = await fetch(GITHUB_API, { headers });
    
    if (!response.ok) {
      if (response.status === 403) {
        console.warn('GitHub API rate limited. Using fallback values.');
      } else {
        console.warn(`GitHub API error: ${response.status}. Using fallback values.`);
      }
      return { stars: 0, forks: 0 };
    }

    const data = await response.json();
    
    return {
      stars: data.stargazers_count || 0,
      forks: data.forks_count || 0,
    };
  } catch (error) {
    console.warn('Failed to fetch GitHub stats:', error.message);
    return { stars: 0, forks: 0 };
  }
}

function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
}

async function main() {
  const stats = await fetchGitHubStats();
  
  const output = {
    stars: stats.stars,
    forks: stats.forks,
    starsFormatted: formatNumber(stats.stars),
    forksFormatted: formatNumber(stats.forks),
    updatedAt: new Date().toISOString(),
  };

  const outputPath = path.join(__dirname, '..', 'src', 'data', 'github-stats.json');
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  
  console.log(`GitHub stats saved: ${stats.stars} stars, ${stats.forks} forks`);
}

main().catch(console.error);