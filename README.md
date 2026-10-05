# Windows development RDP

Temporary Windows Server 2025 development desktop on a standard public GitHub Actions runner (4 vCPU, 16 GB RAM).

Run **Windows development RDP** under Actions. Open the Tailscale login URL in the authorization step and approve the machine. Install Tailscale on your own computer and sign into the same network, then connect using the RDP address shown in the job summary and username `.\seoulsexyking`. The password is stored in the `RDP_PASSWORD` repository secret.

Sessions default to 60 minutes, with a selectable maximum of 330 minutes. The VM and its files disappear after the job ends; save development work externally. Cancel the workflow to finish early. Use only for development and testing of the project associated with this repository. Remove expired development devices in Tailscale if necessary.
