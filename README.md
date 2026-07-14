# chipotle-order-support-agent

A Rasa CALM conversational agent, built and deployed with Rasa Auto.

This repo is a copy of the agent's project for your own ownership and portability —
Rasa Auto deploys it directly to its own hosting, not from this repo.

## What's in this repo

- The full Rasa project (flows, domain, actions, config) for **chipotle-order-support-agent**.
- `Dockerfile` — trains the model at build time and runs both the action
  server and the Rasa core server in one container.
