# Quick Start Guide

## Fastest Way: One Command! ⚡

```bash
./install_all.sh my_migration_project
```

That's it! This installs everything you need.

## Three Simple Steps (Manual)

If you prefer step-by-step control:

### 1️⃣ Install CAO (One-Time Setup)

```bash
python install_cao.py
```

Installs: tmux, uv, and CLI Agent Orchestrator

### 2️⃣ Create Your Project

```bash
python create_project.py my_migration_project
```

Creates: Complete project structure with agents, templates, tools, and LCMP utilities

**Note**: LCMP tools are automatically downloaded and installed during project creation.

### 3️⃣ Install Agents

```bash
cd my_migration_project
python lcmp/install_agents.py
```

Installs: All 28 specialized migration agents

## That's It! 🎉

You're now ready to start your migration project.

## Uninstalling

To remove everything:

```bash
./uninstall_all.sh
```

To reinstall:

```bash
./install_all.sh my_new_project
```

## Common Commands

### List Installed Agents
```bash
cao list
```

### Launch an Agent
```bash
# With Kiro CLI
kiro-cli chat --agent migration_supervisor

# With CAO
cao launch --agents migration_supervisor
```

### Update Agents After Modifications
```bash
python lcmp/install_agents.py
```

### Switch Provider
```bash
python lcmp/install_agents.py --provider q_cli
```

### Update Prompts in Existing Project
```bash
# After modifying prompts in structure/prompts
python update_prompts.py /path/to/my_project
```

## Need Help?

- **Full Guide**: See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- **Scripts Guide**: See [SCRIPTS_GUIDE.md](SCRIPTS_GUIDE.md)
- **Documentation**: See [README.md](README.md)
- **User Guide**: See [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

## Troubleshooting

### CAO Not Found?
```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

### Kiro CLI Authentication Error?
```bash
# If you see "AccessDeniedException" or "bearer token is invalid"
kiro-cli logout
kiro-cli login
```

### Provider Not Available?
```bash
# Install Kiro CLI from https://kiro.ai
# Or use a different provider:
python lcmp/install_agents.py --provider claude_code
```

### Agents Not Installing?
```bash
# Verify CAO is working
cao --help

# Check you're in the project directory
pwd

# Try with verbose output
python lcmp/install_agents.py
```

## Supported Providers

| Provider | CLI Command | Installation |
|----------|-------------|--------------|
| **kiro_cli** (default) | `kiro-cli` | https://kiro.ai |
| **q_cli** | `q` | AWS Documentation |
| **claude_code** | None required | Built-in |

## Project Structure

```
my_migration_project/
├── lcmp/                  # Tools (install_agents.py, validators)
├── agents/              # 28 AI agents in 5 teams
├── input/               # Your legacy code goes here
├── output/              # Generated artifacts
├── templates/           # Report templates
└── prompts/             # AI prompts
```

## Next Steps

1. Add your legacy code to `input/legacy/`
2. Review configuration in `config/paths.cfg`
3. Start with the Migration Supervisor agent
4. Follow the [User Guide](docs/USER_GUIDE.md) for detailed workflows

---

**Remember**: Install CAO once, create many projects! 🚀
