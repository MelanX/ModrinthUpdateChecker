import json
import os
import sys
from datetime import datetime, timezone

import requests

modrinth_projects_url = 'https://api.modrinth.com/v2/projects'
modrinth_version_url = 'https://api.modrinth.com/v2/version'


def get_version_info(version_id: str):
    response = requests.get(f'{modrinth_version_url}/{version_id}')
    if response.status_code == requests.codes.ok:
        return response.json()


def convert_timestamp_to_unix(timestamp: str):
    datetime_object = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    timestamp = datetime_object.replace(tzinfo=timezone.utc).timestamp()
    return int(timestamp)


def build_embeds(project_info: dict, version: dict):
    version_id = version['id']
    version_number = version['version_number']
    date_published = version['date_published']
    game_versions = version['game_versions']
    loaders = version['loaders']
    changelog = version['changelog']
    timestamp = convert_timestamp_to_unix(date_published)
    slug = project_info['slug']

    embed = {
        'title': f'New file released <t:{timestamp}:R>!',
        'author': {
            'name': project_info['title'],
            'url': f'https://modrinth.com/mod/{slug}',
            'icon_url': project_info['icon_url']
        },
        'fields': [
            {
                'name': 'File version',
                'value': f'[{version_number}](https://modrinth.com/mod/{slug}/version/{version_id})',
                'inline': True
            },
            {
                'name': 'Game version' + ('s' if len(game_versions) > 1 else ''),
                'value': '\n'.join(game_versions),
                'inline': True
            },
            {
                'name': 'Loader' + ('s' if len(loaders) > 1 else ''),
                'value': '\n'.join(
                    [f'[{loader.title()}](https://modrinth.com/mods?g=categories:%27{loader}%27)' for loader in
                     loaders]),
                'inline': True
            },
            {
                'name': 'Changelog',
                'value': changelog,
                'inline': False
            }
        ],
        'thumbnail': {
            'url': project_info['icon_url']
        },
        'timestamp': date_published,
        'footer': {
            'icon_url': 'https://cdn.modrinth.com/data/ZrwIGI6c/ca5c1a959e5f23bdc3482c7acbaa1d47ec3a0bd5.png',
            'text': 'Sent by Modrinth Update Checker'
        },
        'color': project_info['color']
    }
    return [embed]


def send_new_version(webhook_url: str, data: dict, project: str, version: str):
    info = get_version_info(version)
    embeds = build_embeds(data[project], info)
    print(json.dumps(embeds))
    msg = {
        'username': 'Modrinth',
        'avatar_url': 'https://cdn.modrinth.com/data/ZrwIGI6c/ca5c1a959e5f23bdc3482c7acbaa1d47ec3a0bd5.png',
        'embeds': embeds
    }
    response = requests.post(webhook_url, json=msg,
                             headers={'Content-Type': 'application/json'})
    print(f'New version "{info['name']}" in "{data[project]['title']}"')
    if response.status_code != requests.codes.ok:
        print(f'Error: {response.text}')


def main(webhook_url: str, projects_file: str):
    with open(projects_file, 'r') as f:
        projects = f.read().split('\n')

    cache = {}
    if os.path.exists('last_checked.json'):
        with open('last_checked.json', 'r') as f:
            cache = json.load(f)

    response = requests.get(modrinth_projects_url,
                            params={'ids': json.dumps(projects)},
                            headers={'User-Agent': 'GitHub@MelanX/ModrinthUpdateChecker',
                                     'Content-Type': 'application/json'}
                            )

    if response.status_code == requests.codes.ok:
        data = {item['slug']: item for item in response.json()}
    else:
        print(f'Error: {response.status_code}\n{response.content}')
        return

    for project in projects:
        if project in cache:
            for version in data[project]['versions']:
                if version not in cache[project]:
                    send_new_version(webhook_url, data, project, version)
        if project not in cache:
            print(f'New project found: {data[project]['title']}')
            cache[project] = data[project]['versions']

    with open('last_checked.json', 'w') as f:
        f.write(json.dumps(cache))


if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print('Please provide a webhook URL and a projects file as command line arguments.')
        sys.exit(os.EX_IOERR)
