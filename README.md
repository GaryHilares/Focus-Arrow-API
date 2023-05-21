## Liberty Arrow Backend

<p align="center">
  <img alt="badge-lastcommit" src="https://img.shields.io/github/last-commit/GaryHilares/Liberty-Arrow-backend?style=for-the-badge">
  <img alt="badge-openissues" src="https://img.shields.io/github/issues-raw/GaryHilares/Liberty-Arrow-backend?style=for-the-badge">
  <img alt="badge-license" src="https://img.shields.io/github/license/GaryHilares/Liberty-Arrow-backend?style=for-the-badge">
  <img alt="badge-contributors" src="https://img.shields.io/github/contributors/GaryHilares/Liberty-Arrow-backend?style=for-the-badge">
  <img alt="badge-codesize" src="https://img.shields.io/github/languages/code-size/GaryHilares/Liberty-Arrow-backend?style=for-the-badge">
</p>

## What is Liberty Arrow Backend?
Liberty Arrow Backend is the backend server for Liberty Arrow. It handles processes such as sending confirmation emails.

### Dependencies
#### Development
- Python 3
- PIP

### Platforms
- API

## Motivation
I wanted to include new features in Liberty Arrow, but they required to have server-side functionality. This is why I created this project as the extension's backend.

## Installation and usage
1. Install dependencies:
    - You can find the latest version of Python 3 and PIP [here](https://www.python.org/downloads/).
2. Setup an email for testing:
    1. Go to [Google Account](https://myaccount.google.com/) and setup 2 factor authentication (2FA) if you do not have one (required for next step).
    2. In Google Account, create an application password for Liberty Arrow Backend (you will only have this option if you have 2FA enabled).
    3. Add your email and application password as the `GMAIL_USERNAME` and `GMAIL_APP_PASSWORD` environment variables, respectively.
3. Run the project:
    1. Fork the repository in GitHub.
    2. Go to your fork and copy the link to clone your repository.
    3. Go to Git in your local machine and use the command `git clone (your link)`.
    4. Run `index.py`.


## Contributors
Thanks to these wonderful people for making Liberty Arrow Backend possible!

<p align="center"><a href="https://github.com/GaryHilares/Liberty-Arrow-backend/graphs/contributors"><img src="https://contrib.rocks/image?repo=GaryHilares/Liberty-Arrow-backend"></a></p>


## License
This work is licensed under a [Creative Commons Attribution 4.0 International License](https://github.com/GaryHilares/Liberty-Arrow-backend/blob/main/LICENSE).