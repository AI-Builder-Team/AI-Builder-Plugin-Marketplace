#!/bin/bash
# tmux-claude session management (single-session pane model)
#
# All panes live in tmux session "work", window 0.
# Pane 0 = driver, Panes 1-8 = workers.
#
# Usage:
#   sessions.sh status              - show all panes with free/busy state
#   sessions.sh state [N]           - detect Claude UI state (IDLE/INFERRING/NO_CLAUDE)
#   sessions.sh free                - list free pane numbers (lowest first)
#   sessions.sh first-free          - print the lowest free pane number
#   sessions.sh launch [N] [DIR] [ARGS] - launch claude in pane N (or first free)
#   sessions.sh quit N              - quit Claude in pane N (Ctrl+C twice)
#   sessions.sh quit-all            - quit Claude in all busy panes
#   sessions.sh send N ["text"]     - send text + Enter (or bare Enter if no text)
#   sessions.sh clear N             - clear Claude's conversation in pane N
#   sessions.sh message N "prompt" [no-qc] - send prompt + verify inference started
#   sessions.sh read N              - capture what's on screen in pane N

SESSION="work"

# Detect pane count dynamically from actual tmux session
_detect_panes() {
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    local count
    count=$(tmux list-panes -t "$SESSION:0" -F '#{pane_index}' 2>/dev/null | wc -l | tr -d ' ')
    # Subtract 1 for driver pane 0
    local max=$(( count - 1 ))
    seq 1 "$max"
  else
    # Fallback: default to 8 workers
    seq 1 8
  fi
}
PANES=$(_detect_panes)

target() {
  echo "${SESSION}:0.$1"
}

pane_exists() {
  tmux display-message -t "$(target "$1")" -p '' 2>/dev/null
}

pane_pid() {
  tmux display-message -t "$(target "$1")" -p '#{pane_pid}' 2>/dev/null
}

is_free() {
  local s="$1"
  pane_exists "$s" || return 1
  local pid
  pid=$(pane_pid "$s")
  [ -z "$pid" ] && return 1
  ! pgrep -P "$pid" >/dev/null 2>&1
}

has_claude() {
  local s="$1"
  local pid
  pid=$(pane_pid "$s")
  [ -z "$pid" ] && return 1
  pgrep -P "$pid" -x claude >/dev/null 2>&1
}

cmd_status() {
  if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "Session '$SESSION' not running. Launch with: bash scripts/launch.sh"
    return 1
  fi
  for s in $PANES; do
    if ! pane_exists "$s"; then
      echo "$s: MISSING"
    elif has_claude "$s"; then
      echo "$s: BUSY (claude)"
    elif ! is_free "$s"; then
      local pid cmd_name
      pid=$(pane_pid "$s")
      cmd_name=$(pgrep -P "$pid" | head -1 | xargs -I{} ps -o comm= -p {} 2>/dev/null)
      echo "$s: BUSY ($cmd_name)"
    else
      echo "$s: FREE"
    fi
  done
}

cmd_free() {
  for s in $PANES; do
    is_free "$s" && echo "$s"
  done
}

cmd_first_free() {
  for s in $PANES; do
    if is_free "$s"; then
      echo "$s"
      return 0
    fi
  done
  echo "NONE"
  return 1
}

cmd_launch() {
  local pane="$1"
  local dir="$2"
  local args="$3"

  if [ -z "$pane" ]; then
    pane=$(cmd_first_free)
    if [ "$pane" = "NONE" ]; then
      echo "ERROR: No free panes available"
      return 1
    fi
  fi

  if ! is_free "$pane"; then
    echo "ERROR: Pane $pane is busy"
    return 1
  fi

  local t
  t=$(target "$pane")

  # Clear any garbage on the prompt
  tmux send-keys -t "$t" C-c
  sleep 0.2

  if [ -n "$dir" ]; then
    tmux send-keys -t "$t" "cd $(printf '%q' "$dir")" Enter
    sleep 0.3
  fi

  local cmd="env -u CLAUDECODE claude --dangerously-skip-permissions"
  if [ -n "$args" ]; then
    cmd="$cmd $args"
  fi
  tmux send-keys -t "$t" "$cmd" Enter
  echo "Launched in pane $pane"
}

cmd_quit() {
  local pane="$1"
  if [ -z "$pane" ]; then
    echo "ERROR: Specify pane number"
    return 1
  fi
  local t
  t=$(target "$pane")

  if is_free "$pane"; then
    echo "Pane $pane is already free"
    return 0
  fi
  if has_claude "$pane"; then
    tmux send-keys -t "$t" C-c
    sleep 0.5
    tmux send-keys -t "$t" C-c
    echo "Quit Claude in pane $pane"
  else
    tmux send-keys -t "$t" C-c
    echo "Quit process in pane $pane"
  fi
}

cmd_quit_all() {
  for s in $PANES; do
    if ! is_free "$s"; then
      cmd_quit "$s"
    fi
  done
}

cmd_send() {
  local pane="$1"
  local text="$2"
  if [ -z "$pane" ]; then
    echo "ERROR: Usage: sessions.sh send N [\"text\"]"
    return 1
  fi
  if [ -z "$text" ]; then
    # Bare Enter — useful when pasted text needs a second Enter to submit
    tmux send-keys -t "$(target "$pane")" Enter
    echo "Sent Enter to pane $pane"
  else
    tmux send-keys -t "$(target "$pane")" "$text" Enter
    echo "Sent to pane $pane"
  fi
}

_prep_input() {
  local t
  t=$(target "$1")
  tmux send-keys -t "$t" Escape
  sleep 0.1
  tmux send-keys -t "$t" C-l
  sleep 0.1
  tmux send-keys -t "$t" i
  sleep 0.1
}

cmd_clear() {
  local pane="$1"
  if [ -z "$pane" ]; then
    echo "ERROR: Specify pane number"
    return 1
  fi
  _prep_input "$pane"
  tmux send-keys -t "$(target "$pane")" -l '/clear'
  tmux send-keys -t "$(target "$pane")" Enter
  echo "Cleared Claude conversation in pane $pane"
}

cmd_message() {
  local pane="$1"
  local prompt="$2"
  local skip_qc="$3"  # pass "no-qc" to skip verification
  if [ -z "$pane" ] || [ -z "$prompt" ]; then
    echo "ERROR: Usage: sessions.sh message N \"prompt\" [no-qc]"
    return 1
  fi

  # Snapshot screen before sending for QC comparison
  local before_snapshot
  before_snapshot=$(tmux capture-pane -t "$(target "$pane")" -p)

  _prep_input "$pane"
  tmux send-keys -t "$(target "$pane")" -l "$prompt"
  tmux send-keys -t "$(target "$pane")" Enter
  echo "Sent prompt to Claude in pane $pane"

  if [ "$skip_qc" != "no-qc" ]; then
    _qc_message_sent "$pane" "$before_snapshot"
  fi
}

cmd_read() {
  local pane="$1"
  if [ -z "$pane" ]; then
    echo "ERROR: Specify pane number"
    return 1
  fi
  tmux capture-pane -t "$(target "$pane")" -p
}

# Detect if Claude is actively inferring.
#
# Signal: animated asterisk markers in non-gray color = inference in progress.
# Claude cycles through 5 asterisk chars during inference: ✢ ✳ ✶ ✻ ✽
# After completion, these same chars appear in gray rgb(153,153,153) on the
# "Cogitated/Brewed/Baked/Churned for..." line. Gray = done, anything else = active.
# Returns: INFERRING | IDLE | NO_CLAUDE
_pane_ui_state() {
  local pane="$1"
  if ! has_claude "$pane"; then
    echo "NO_CLAUDE"
    return
  fi

  # Animation chars ✢✳✶✻✽ on screen = inferring, unless only in gray (completion line)
  # Claude Code may use truecolor (38;2;R;G;B) or 256-color (38;5;N) escapes.
  # Sample 3 times over ~300ms to cover animation frame gaps
  local t_pane
  t_pane=$(target "$pane")
  local attempt
  for attempt in 1 2 3; do
    if tmux capture-pane -t "$t_pane" -e -p | perl -e \
      'use utf8; binmode(STDIN, ":utf8");
      # 256-color indices considered gray (approximate)
      my %gray256 = map {$_ => 1} (7, 8, 145, 146, 148, 150, 153, 188, 231,
                                    232..255, 240..250);
      while(<>){
        next unless /[\x{2722}\x{2733}\x{2736}\x{273B}\x{273D}]/;
        # Truecolor: 38;2;R;G;B
        my @rgb = /38;2;(\d+;\d+;\d+)/g;
        for my $c (@rgb){
          exit 0 unless $c eq "153;153;153";
        }
        # 256-color: 38;5;N
        my @c256 = /38;5;(\d+)/g;
        for my $n (@c256){
          exit 0 unless $gray256{$n};
        }
      } exit 1'; then
      echo "INFERRING"
      return
    fi
    [ "$attempt" -lt 3 ] && sleep 0.15
  done

  echo "IDLE"
}

cmd_state() {
  local pane="$1"
  if [ -z "$pane" ]; then
    # Parallel state check across all panes
    local tmpdir
    tmpdir=$(mktemp -d)
    for s in $PANES; do
      (
        if has_claude "$s"; then
          echo "$s: $(_pane_ui_state "$s")"
        elif is_free "$s"; then
          echo "$s: FREE"
        else
          echo "$s: BUSY (other)"
        fi
      ) > "$tmpdir/$s" &
    done
    wait
    for s in $PANES; do
      cat "$tmpdir/$s"
    done
    rm -rf "$tmpdir"
  else
    _pane_ui_state "$pane"
  fi
}

# Verify Claude started after a message. Long pastes sometimes need
# a second Enter. Compares screen before/after to avoid false retries.
_qc_message_sent() {
  local pane="$1"
  local before_snapshot="$2"  # screen content captured before sending
  local max_attempts=3
  local poll_interval=2
  local attempt=0
  local state

  while [ $attempt -lt $max_attempts ]; do
    sleep "$poll_interval"
    state=$(_pane_ui_state "$pane")

    if [ "$state" = "INFERRING" ]; then
      echo "$state"
      return 0
    fi

    attempt=$((attempt + 1))

    if [ $attempt -lt $max_attempts ]; then
      # Not inferring yet — send an extra Enter (long pastes often swallow the first one)
      tmux send-keys -t "$(target "$pane")" Enter
      echo "QC: Sent extra Enter to pane $pane (attempt $attempt, state=$state)"
    fi
  done

  # Exhausted retries — report final state so the caller can see it
  echo "$state"
  if [ "$state" != "INFERRING" ]; then
    echo "QC WARNING: Pane $pane did not start inferring after $max_attempts checks"
    return 1
  fi
}

case "${1:-status}" in
  status)     cmd_status ;;
  state)      cmd_state "$2" ;;
  free)       cmd_free ;;
  first-free) cmd_first_free ;;
  launch)     cmd_launch "$2" "$3" "$4" ;;
  quit)       cmd_quit "$2" ;;
  quit-all)   cmd_quit_all ;;
  send)       cmd_send "$2" "$3" ;;
  clear)      cmd_clear "$2" ;;
  message)    cmd_message "$2" "$3" "$4" ;;
  read)       cmd_read "$2" ;;
  *)          echo "Unknown command: $1"; exit 1 ;;
esac
