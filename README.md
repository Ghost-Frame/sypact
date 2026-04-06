# sypact

Agent trust library where opaque credential handling is a property of everything.

Agents operate with full capability but zero visibility into the secrets that power them. Credentials are resolved at point of use through opaque handles -- the LLM never sees raw secret material.

## Install

```bash
pip install sypact
```

## Quick Start

```python
from sypact import CredentialHandle, EnvBackend

backend = EnvBackend()
handle = backend.store("API_KEY", "sk-secret-value")

# The handle is safe to pass around -- it never exposes the secret
print(handle)  # <sypact:default/API_KEY>

# Secret is resolved only at point of use
secret = backend.resolve(handle)
```

## Architecture

sypact is built in four layers, each adding a level of trust:

- **Layer 0** : Credential handles and pluggable secret backends
- **Layer 1** : Agent identity (human-delegated certificates)
- **Layer 2** : Mutual authentication (challenge-response between agents)
- **Layer 3** : Capability negotiation ("I can do X, what can you do?")
- **Layer 4** :Trust scoring (behavioral reputation over time)

## License

MIT
