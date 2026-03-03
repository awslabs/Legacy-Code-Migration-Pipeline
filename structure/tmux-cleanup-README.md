# tmux-cleanup.sh

Clean up inactive tmux windows based on activity threshold.

## Parameters

```
-t, --threshold HOURS    Inactivity threshold in hours (default: 1)
-a, --auto               Auto mode: delete without confirmation
--delete-all             Delete all inactive windows automatically
-h, --help               Show help message
```

## Usage Examples

```bash
./tmux-cleanup.sh              # Interactive, 1h threshold
./tmux-cleanup.sh -t 2         # Interactive, 2h threshold  
./tmux-cleanup.sh -t 4 -a      # Auto delete windows inactive >4h
./tmux-cleanup.sh -t 6 --delete-all  # Auto delete all inactive >6h
```

## Automated Cleanup

Add to crontab for periodic cleanup:

```bash
# Run every hour, delete windows inactive >4 hours
0 * * * * /path/to/tmux-cleanup.sh -t 4 -a
```

## Safety

- Never deletes the last window in a session
- Interactive mode shows all windows before deletion
- Can delete individual windows by ID or all at once
