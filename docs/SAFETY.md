# Safety design

Browser automation can accidentally cross from information retrieval into real-world side effects. This project therefore separates:

- navigation and inspection — allowed;
- form filling and reversible interaction — allowed;
- final order/payment submission — blocked from unrestricted MCP execution.

A production deployment should add authentication, per-user sessions, domain allowlists, stronger action schemas, CSRF protection, secret isolation, rate limits, and an explicit approval UI before any irreversible action.
