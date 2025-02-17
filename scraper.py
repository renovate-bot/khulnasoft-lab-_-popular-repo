# coding:utf-8

import datetime
import subprocess
import requests
import os
import codecs
from pyquery import PyQuery as pq


def git_add_commit_push(date, filename):
    """Add, commit, and push changes to Git."""
    commands = [
        f'git add {filename}',
        f'git commit -m "{date}"',
        'git push -u origin master'
    ]
    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True)


def create_markdown(date, filename):
    """Create a markdown file with the current date."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"## {date}\n")


def scrape(language, filename):
    """Scrape trending GitHub repositories for a given language and append to a markdown file."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }

    url = f'https://github.com/trending/{language}'
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return

    doc = pq(response.content)
    items = doc('div.Box article.Box-row')

    with codecs.open(filename, "a", "utf-8") as f:
        f.write(f'\n#### {language}\n')

        for item in items:
            i = pq(item)
            title = i(".lh-condensed a").text()
            owner = i(".lh-condensed span.text-normal").text().strip()
            description = i("p.col-9").text().strip()
            repo_url = f"https://github.com{i('.lh-condensed a').attr('href')}"

            if title and repo_url:
                f.write(f"* [{title}]({repo_url}): {description if description else 'No description'}\n")


def job():
    """Main job to create markdown, scrape GitHub trends, and push to Git."""
    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f'{strdate}.md'

    create_markdown(strdate, filename)

    # Scrape GitHub trends for different languages
    for lang in ['python', 'swift', 'javascript', 'go']:
        scrape(lang, filename)

    # Uncomment this if you want to push changes to GitHub
    # git_add_commit_push(strdate, filename)


if __name__ == '__main__':
    job()
