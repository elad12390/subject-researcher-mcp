# Security Policy

## Reporting Security Vulnerabilities

Report vulnerabilities to `security@progressus-software.com`. Do not file public issues for suspected vulnerabilities.

We acknowledge within 2 business days. Supported versions: latest two minor releases.

## Security Practices

This MCP server follows secure development practices:

- **No customer data**: This tool processes only publicly available research data
- **API key security**: Bring your own API keys - we don't store or transmit them
- **Input validation**: All user inputs are validated and sanitized
- **Rate limiting**: Built-in rate limiting to prevent abuse
- **Container security**: Docker image runs as non-root user

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Security Features

- **Secret scanning**: Automated secret detection in CI/CD
- **Dependency scanning**: Regular vulnerability audits
- **Container scanning**: Docker image security scanning
- **Code analysis**: Static analysis for security issues

## Best Practices for Users

- Keep your API keys secure and never commit them to version control
- Use the provided `.env.example` as a template for local configuration
- Update to the latest version regularly for security patches
- Report any suspicious behavior or potential vulnerabilities