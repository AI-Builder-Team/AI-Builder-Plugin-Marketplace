#!/bin/bash
# Launch the tmux workstation in Ghostty with a 1 + NxN grid layout.
#
# Usage: launch.sh [8|10|12]   (default: 8)
#
# 8-pane layout (4x2 grid):
#   ┌──────┬─────┬─────┬─────┬─────┐
#   │      │  1  │  2  │  3  │  4  │
#   │  0   ├─────┼─────┼─────┼─────┤
#   │      │  5  │  6  │  7  │  8  │
#   └──────┴─────┴─────┴─────┴─────┘
#
# 10-pane layout (5x2 grid):
#   ┌──────┬────┬────┬────┬────┬────┐
#   │      │  1 │  2 │  3 │  4 │  5 │
#   │  0   ├────┼────┼────┼────┼────┤
#   │      │  6 │  7 │  8 │  9 │ 10 │
#   └──────┴────┴────┴────┴────┴────┘
#
# 12-pane layout (6x2 grid):
#   ┌──────┬───┬───┬───┬───┬───┬───┐
#   │      │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │
#   │  0   ├───┼───┼───┼───┼───┼───┤
#   │      │ 7 │ 8 │ 9 │10 │11 │12 │
#   └──────┴───┴───┴───┴───┴───┴───┘
#
# Pane 0: driver pane (full height, left)
# Remaining: worker panes in grid

SESSION="work"
GRID="${1:-8}"

if [ "$GRID" != "8" ] && [ "$GRID" != "10" ] && [ "$GRID" != "12" ]; then
  echo "Usage: launch.sh [8|10|12]  (default: 8)"
  exit 1
fi

# Kill existing session if present
tmux kill-session -t "$SESSION" 2>/dev/null

# Launch Ghostty with a new tmux session
ghostty -e tmux new-session -s "$SESSION" &
sleep 1.5

# Split left | right (left ~20%, right ~80%)
tmux split-window -h -t "$SESSION:0.0" -p 80

# Split right into top and bottom rows
tmux split-window -v -t "$SESSION:0.1" -p 50

if [ "$GRID" = "8" ]; then
  # Top row: split pane 1 into 4 equal columns
  tmux split-window -h -t "$SESSION:0.1" -p 75
  tmux split-window -h -t "$SESSION:0.2" -p 67
  tmux split-window -h -t "$SESSION:0.3" -p 50

  # Bottom row: split pane 5 into 4 equal columns
  tmux split-window -h -t "$SESSION:0.5" -p 75
  tmux split-window -h -t "$SESSION:0.6" -p 67
  tmux split-window -h -t "$SESSION:0.7" -p 50

  echo "Workstation launched: session '$SESSION' with 9 panes (0=driver, 1-8=workers)"

elif [ "$GRID" = "10" ]; then
  # Top row: split pane 1 into 5 equal columns
  tmux split-window -h -t "$SESSION:0.1" -p 80
  tmux split-window -h -t "$SESSION:0.2" -p 75
  tmux split-window -h -t "$SESSION:0.3" -p 67
  tmux split-window -h -t "$SESSION:0.4" -p 50

  # Bottom row: split pane 6 into 5 equal columns
  tmux split-window -h -t "$SESSION:0.6" -p 80
  tmux split-window -h -t "$SESSION:0.7" -p 75
  tmux split-window -h -t "$SESSION:0.8" -p 67
  tmux split-window -h -t "$SESSION:0.9" -p 50

  echo "Workstation launched: session '$SESSION' with 11 panes (0=driver, 1-10=workers)"

elif [ "$GRID" = "12" ]; then
  # Top row: split pane 1 into 6 equal columns
  # Percentages: 83 (5/6), 80 (4/5), 75 (3/4), 67 (2/3), 50 (1/2)
  tmux split-window -h -t "$SESSION:0.1" -p 83
  tmux split-window -h -t "$SESSION:0.2" -p 80
  tmux split-window -h -t "$SESSION:0.3" -p 75
  tmux split-window -h -t "$SESSION:0.4" -p 67
  tmux split-window -h -t "$SESSION:0.5" -p 50

  # Bottom row: split pane 7 into 6 equal columns
  tmux split-window -h -t "$SESSION:0.7" -p 83
  tmux split-window -h -t "$SESSION:0.8" -p 80
  tmux split-window -h -t "$SESSION:0.9" -p 75
  tmux split-window -h -t "$SESSION:0.10" -p 67
  tmux split-window -h -t "$SESSION:0.11" -p 50

  echo "Workstation launched: session '$SESSION' with 13 panes (0=driver, 1-12=workers)"
fi

# Select the driver pane
tmux select-pane -t "$SESSION:0.0"
