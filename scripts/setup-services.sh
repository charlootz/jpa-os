#!/bin/bash
# Setup jpa-os background services on macOS

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "Setting up jpa-os services..."

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Copy plist files
echo "Installing launchd services..."
cp "$SCRIPT_DIR/com.jpa-os.scheduler.plist" "$LAUNCH_AGENTS/"
cp "$SCRIPT_DIR/com.jpa-os.slack.plist" "$LAUNCH_AGENTS/"

# Load services
echo "Loading services..."
launchctl load "$LAUNCH_AGENTS/com.jpa-os.scheduler.plist" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS/com.jpa-os.slack.plist" 2>/dev/null || true

echo ""
echo "Services installed. Status:"
echo ""
echo "Scheduler:"
launchctl list | grep jpa-os.scheduler || echo "  Not running (check logs)"
echo ""
echo "Slack:"
launchctl list | grep jpa-os.slack || echo "  Not running (check logs)"
echo ""
echo "Logs at: $PROJECT_DIR/logs/"
echo ""
echo "Commands:"
echo "  Stop scheduler:  launchctl unload ~/Library/LaunchAgents/com.jpa-os.scheduler.plist"
echo "  Start scheduler: launchctl load ~/Library/LaunchAgents/com.jpa-os.scheduler.plist"
echo "  Stop slack:      launchctl unload ~/Library/LaunchAgents/com.jpa-os.slack.plist"
echo "  Start slack:     launchctl load ~/Library/LaunchAgents/com.jpa-os.slack.plist"
echo "  View logs:       tail -f $PROJECT_DIR/logs/scheduler.log"
