import json
import os
import sys
from datetime import datetime, timezone

import requests

modrinth_projects_url = 'https://api.modrinth.com/v2/projects'
modrinth_version_url = 'https://api.modrinth.com/v2/version'


def version_info(version_id: str):
    response = requests.get(f'{modrinth_version_url}/{version_id}')
    if response.status_code == requests.codes.ok:
        return response.json()


def get_timestamp(timestamp: str):
    datetime_object = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Convert to Unix timestamp
    timestamp = datetime_object.replace(tzinfo=timezone.utc).timestamp()
    return int(timestamp)


def build_embeds(project_info: dict, version_info: dict):
    timestamp = get_timestamp(version_info['date_published'])
    return [
        {
            'title': f'New file released <t:{timestamp}:R>!',
            'author': {
                'name': project_info['title'],
                'url': f'https://modrinth.com/mod/{project_info['slug']}',
                'icon_url': project_info['icon_url']
            },
            'fields': [
                {
                    'name': 'File version',
                    'value': f'[{version_info['version_number']}](https://modrinth.com/mod/{project_info['slug']}/version/{version_info['id']})',
                    'inline': True
                },
                {
                    'name': 'Game version' + ('s' if len(version_info['game_versions']) > 1 else ''),
                    'value': '\n'.join(version_info['game_versions']),
                    'inline': True
                },
                {
                    'name': 'Loader' + ('s' if len(version_info['loaders']) > 1 else ''),
                    'value': '\n'.join(
                        [f'[{loader.title()}](https://modrinth.com/mods?g=categories:%27{loader}%27)' for loader in
                         version_info['loaders']]),
                    'inline': True
                },
                {
                    'name': 'Changelog',
                    'value': version_info['changelog'],
                    'inline': False
                }
            ],
            'thumbnail': {
                'url': project_info['icon_url']
            },
            'timestamp': version_info['date_published'],
            'footer': {
                'icon_url': 'https://cdn.modrinth.com/data/ZrwIGI6c/ca5c1a959e5f23bdc3482c7acbaa1d47ec3a0bd5.png',
                'text': 'Sent by Modrinth Update Checker'
            },
            'color': project_info['color']
        }
    ]


def main(webhook_url: str):
    with open('projects.txt', 'r') as f:
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
                    info = version_info(version)
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
        if project not in cache:
            print(f'New project found: {data[project]['title']}')
            cache[project] = data[project]['versions']

    with open('last_checked.json', 'w') as f:
        f.write(json.dumps(cache))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Please provide a webhook URL as a command line argument.')
        sys.exit(os.EX_IOERR)
