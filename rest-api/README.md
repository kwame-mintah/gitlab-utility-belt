# REST API

This directory makes use of the [REST API](https://docs.gitlab.com/ee/api/rest/index.html) and requires a personal
access token (PAT) to be created beforehand. Each utility file in this directory will list scopes needed to be enabled
for the PAT.

## Creating a PAT

1. In the upper-right corner, select your avatar.
2. Select Edit profile.
3. On the left sidebar, select Access Tokens.
4. Enter a name and expiry date for the token.
5. Select the desired scopes.
6. Select Create personal access token.
7. Save the personal access token somewhere safe. After you leave the page, you no longer have access to the token.

> :books: **Note:** *[GitLab Docs](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html).*

## Environment variables

| Environment Variable | Description                   | Example                |
|----------------------|-------------------------------|------------------------|
| GITLAB_API_TOKEN     | The users PAT token           | glpat-AbcDeFGHIJ_kLmNP |
| GITLAB_DOMAIN_NAME   | The GitLab server domain name | gitlab.com             |

## Utilities

| Filename             | Purpose                                            | PAT Scope(s)            |
|----------------------|----------------------------------------------------|-------------------------|
| `gitlab-clone-repos` | Clones all repositories that is visible to a user. | `api` `read_repository` |

## Troubleshooting

### Failed to clone due to exit code: 128

If you're getting this error, please make sure your ssh key is valid and that you have the necessary rights to
access the repository being cloned.
