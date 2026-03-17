#!/bin/bash
# Equalize all columns in the work session layout.
# Detects 8-pane (5 cols), 10-pane (6 cols), or 12-pane (7 cols) layout automatically.

SESSION="work"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "Session '$SESSION' not running."
  exit 1
fi

# Count panes to determine layout
pane_count=$(tmux list-panes -t "$SESSION:0" -F '#{pane_index}' | wc -l | tr -d ' ')
total=$(tmux display-message -t "$SESSION:0" -p '#{window_width}')

if [ "$pane_count" -eq 13 ]; then
  # 12-pane layout: 7 columns (driver + 6 per row), 6 separators
  cols=7
  w=$(( (total - 6) / 7 ))
  tmux resize-pane -t "$SESSION:0.0" -x "$w"
  for i in 1 2 3 4 5 7 8 9 10 11; do
    tmux resize-pane -t "$SESSION:0.$i" -x "$w"
  done
elif [ "$pane_count" -eq 11 ]; then
  # 10-pane layout: 6 columns (driver + 5 per row), 5 separators
  cols=6
  w=$(( (total - 5) / 6 ))
  tmux resize-pane -t "$SESSION:0.0" -x "$w"
  for i in 1 2 3 4 6 7 8 9; do
    tmux resize-pane -t "$SESSION:0.$i" -x "$w"
  done
else
  # 8-pane layout: 5 columns (driver + 4 per row), 4 separators
  cols=5
  w=$(( (total - 4) / 5 ))
  tmux resize-pane -t "$SESSION:0.0" -x "$w"
  for i in 1 2 3 5 6 7; do
    tmux resize-pane -t "$SESSION:0.$i" -x "$w"
  done
fi

echo "Equalized: $cols columns at ${w}w each (window ${total}w)"
