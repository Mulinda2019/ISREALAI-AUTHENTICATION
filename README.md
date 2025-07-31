# ISREALAI Technologies Authentication Project

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.10+-blue)

## Overview

This Flask-based authentication system by ISREALAI Technologies provides a secure, modular, and scalable solution for user management and authentication.

## Features

- User registration, login, logout, and password reset flows
- Password hashing and verification with Flask-Bcrypt
- Email verification and password reset emails via Flask-Mail
- Role-based access control (admin, user)
- SQLite backend using SQLAlchemy ORM
- Docker support for containerized deployments
- Environment variable-based configuration for security and flexibility

## Requirements

- Python 3.10+
- Flask 2.2+
- Flask-SQLAlchemy 2.5+
- Flask-Bcrypt 1.0+
- Flask-Mail 0.9+
- Other dependencies as listed in `requirements.txt`

## Installation

Clone the repository and set up your environment:

```bash
git clone https://github.com/your-repo/isrealai-auth.git
cd isrealai-auth
python -m venv venv
source venv/bin/activate          # On Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
