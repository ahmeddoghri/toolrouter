# Security Policy

## Supported versions

This project is pre-1.0. Security fixes land on `main`; track the latest commit.

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's
[private vulnerability reporting](https://github.com/ahmeddoghri/toolrouter/security/advisories/new)
or email the maintainer. Include a description of the issue and its impact,
steps to reproduce (a minimal proof-of-concept helps), and any suggested fix.

You can expect an acknowledgement within a few days. Once a fix is out you will
be credited unless you would rather stay anonymous.

## Scope notes

toolrouter is a pure-stdlib library with no runtime dependencies and makes no
network calls. It scores text against a tool registry, so the main thing to
watch is that tool descriptions and queries you feed it may come from untrusted
sources. The router only ever returns a tool name or an abstention; it never
executes anything. Executing the chosen tool, and sandboxing that execution, is
your responsibility.
