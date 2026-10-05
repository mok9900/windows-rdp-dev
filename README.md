# Windows development RDP

Temporary Windows Server 2025 development desktop on a standard public GitHub Actions runner (4 vCPU, 16 GB RAM).

Run **Windows development RDP** under Actions after the workspace gateway starts. Windows opens authenticated outbound HTTPS/WebSocket connections to the gateway. The gateway relays native RDP TCP bytes; connect with an ordinary RDP client and username `.\seoulsexyking`. No Tailscale client is used. The password is stored in the `RDP_PASSWORD` repository secret. `RELAY_URL` and `RELAY_TOKEN` are gateway secrets, and must be updated when its public endpoint changes. The workspace gateway must remain running throughout the session.

Sessions default to 60 minutes, with a selectable maximum of 330 minutes. The VM and its files disappear after the job ends; save development work externally. Cancel the workflow to finish early. Use only for development and testing of the project associated with this repository. Remove expired development devices in Tailscale if necessary.
