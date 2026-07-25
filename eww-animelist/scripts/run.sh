#!/usr/bin/env bash
#
# run.sh — setup/launcher for eww-animelist
#
# Usage:
#   chmod +x run.sh
#   ./run.sh
#
set -euo pipefail
# ---------------------------------------------------------------------------
# CONFIG — adjust these paths to match your eww config
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EWW_CONFIG_DIR="${EWW_CONFIG_DIR:-$HOME/.config/eww}"   # where eww.yuck/eww.scss live
DARK_SCSS="$EWW_CONFIG_DIR/eww-dark.scss"                     # your dark stylesheet
LIGHT_SCSS="$EWW_CONFIG_DIR/eww-light.scss"               # your light stylesheet
ACTIVE_SCSS="$EWW_CONFIG_DIR/eww.scss"                  # the file eww.yuck actually @imports
ANIME_WIDGET="anime-widget"                                # eww window name to open
CACHE_DIR="$SCRIPT_DIR/../cache"
CODE_FILE="$CACHE_DIR/code.txt"
# Terminal emulator to spawn background scripts in.
# Override with: TERMINAL=alacritty ./run.sh
TERMINAL="${TERMINAL:-}"
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    source .venv/bin/activate
    pip install flask image requests dotenv
else
    source .venv/bin/activate
fi
log() { echo -e "\033[1;34m[run.sh]\033[0m $*"; }
err() { echo -e "\033[1;31m[run.sh]\033[0m $*" >&2; }
# Pick an available terminal emulator if not explicitly set
detect_terminal() {
    if [ -n "$TERMINAL" ]; then
        return
    fi
    for t in kitty alacritty foot gnome-terminal konsole xterm; do
        if command -v "$t" >/dev/null 2>&1; then
            TERMINAL="$t"
            return
        fi
    done
    err "No supported terminal emulator found. Set TERMINAL=<your-terminal> and rerun."
    exit 1
}
# Spawn a command in a new terminal window, in $SCRIPT_DIR
spawn_terminal() {
    local title="$1"
    local cmd="$2"
    case "$TERMINAL" in
        kitty)
            kitty --title "$title" --directory "$SCRIPT_DIR" bash -c "$cmd; exec bash" &
            ;;
        alacritty)
            alacritty --title "$title" --working-directory "$SCRIPT_DIR" -e bash -c "$cmd; exec bash" &
            ;;
        foot)
            foot --title="$title" -D "$SCRIPT_DIR" bash -c "$cmd; exec bash" &
            ;;
        gnome-terminal)
            gnome-terminal --title="$title" --working-directory="$SCRIPT_DIR" -- bash -c "$cmd; exec bash" &
            ;;
        konsole)
            konsole --new-tab -p tabtitle="$title" --workdir "$SCRIPT_DIR" -e bash -c "$cmd; exec bash" &
            ;;
        xterm)
            xterm -T "$title" -e bash -c "cd '$SCRIPT_DIR' && $cmd; exec bash" &
            ;;
        *)
            err "Unsupported terminal: $TERMINAL"
            exit 1
            ;;
    esac
}
# ---------------------------------------------------------------------------
# 0. Credentials — ask user for client_id and client_secret, patch py files
# ---------------------------------------------------------------------------
setup_credentials() {
    local creds_file="$CACHE_DIR/.credentials"
    mkdir -p "$CACHE_DIR"
    # If credentials were saved from a previous run, reuse them
    if [ -f "$creds_file" ]; then
        source "$creds_file"
        log "Using saved credentials (client_id: ${CLIENT_ID:0:8}...)"
        log "To reset credentials, delete: $creds_file"
    else
        echo ""
        log "Enter your MyAnimeList API credentials."
        log "You can get them at: https://myanimelist.net/apiconfig"
        echo ""
        while true; do
            read -rp "  Client ID     : " CLIENT_ID
            CLIENT_ID="${CLIENT_ID// /}"   # strip accidental spaces
            if [ -n "$CLIENT_ID" ]; then
                break
            fi
            err "Client ID cannot be empty."
        done
        while true; do
            read -rp "  Client Secret : " CLIENT_SECRET
            CLIENT_SECRET="${CLIENT_SECRET// /}"
            if [ -n "$CLIENT_SECRET" ]; then
                break
            fi
            err "Client Secret cannot be empty."
        done
        echo ""
        # Save for future runs
        cat > "$creds_file" <<EOF
CLIENT_ID="$CLIENT_ID"
CLIENT_SECRET="$CLIENT_SECRET"
EOF
        chmod 600 "$creds_file"
        log "Credentials saved to $creds_file"
    fi
	# Patch get_token.py
    sed -i \
        -e "s|^client_id\s*=\s*\".*\"|client_id = \"$CLIENT_ID\"|" \
        -e "s|^client_secret\s*=\s*\".*\"|client_secret = \"$CLIENT_SECRET\"|" \
        "$SCRIPT_DIR/get_token.py"
    # Patch oauth.py
    if grep -q "^client_id\s*=" "$SCRIPT_DIR/oauth.py" 2>/dev/null; then
        sed -i \
            -e "s|^client_id\s*=\s*\".*\"|client_id = \"$CLIENT_ID\"|" \
            -e "s|^client_secret\s*=\s*\".*\"|client_secret = \"$CLIENT_SECRET\"|" \
            "$SCRIPT_DIR/oauth.py"
    fi
    # Patch auth.py
    if grep -q "^client_id\s*=" "$SCRIPT_DIR/auth.py" 2>/dev/null; then
        sed -i \
            -e "s|^client_id\s*=\s*\".*\"|client_id = \"$CLIENT_ID\"|" \
            -e "s|^client_secret\s*=\s*\".*\"|client_secret = \"$CLIENT_SECRET\"|" \
            "$SCRIPT_DIR/auth.py"
    fi
	# Patch update_widget.py
    if grep -q "^CLIENT_ID\s*=" "$SCRIPT_DIR/update_widget.py" 2>/dev/null; then
        sed -i \
            -e "s|^CLIENT_ID\s*=\s*\".*\"|CLIENT_ID = \"$CLIENT_ID\"|" \
            -e "s|^CLIENT_SECRET\s*=\s*\".*\"|CLIENT_SECRET = \"$CLIENT_SECRET\"|" \
            "$SCRIPT_DIR/update_widget.py"
    fi
    log "Credentials applied to Python scripts."
    log "Credentials applied to Python scripts."
    echo ""
}
# ---------------------------------------------------------------------------
# 1. Ask light or dark mode
# ---------------------------------------------------------------------------
choose_theme() {
    log "Choose a theme:"
    select mode in "Dark mode" "Light mode"; do
        case "$mode" in
            "Dark mode")
                THEME="dark"
                break
                ;;
            "Light mode")
                THEME="light"
                break
                ;;
            *)
                echo "Invalid choice, pick 1 or 2."
                ;;
        esac
    done
}
apply_theme() {
    if [ "$THEME" = "dark" ]; then
        if [ ! -f "$DARK_SCSS" ]; then
            err "Dark stylesheet not found: $DARK_SCSS"
            exit 1
        fi
        log "Applying dark mode ($DARK_SCSS -> $ACTIVE_SCSS)"
        cp -f "$DARK_SCSS" "$ACTIVE_SCSS"
    else
        if [ ! -f "$LIGHT_SCSS" ]; then
            err "Light stylesheet not found: $LIGHT_SCSS"
            exit 1
        fi
        log "Applying light mode ($LIGHT_SCSS -> $ACTIVE_SCSS)"
        cp -f "$LIGHT_SCSS" "$ACTIVE_SCSS"
    fi
}
# ---------------------------------------------------------------------------
# 1b. Ask which list source to use            [NEW]
# ---------------------------------------------------------------------------
choose_source() {
    log "Choose a list source:"
    select src in "MyAnimeList" "AniList"; do
        case "$src" in
            "MyAnimeList")
                SOURCE="mal"
                break
                ;;
            "AniList")
                SOURCE="anilist"
                break
                ;;
            *)
                echo "Invalid choice, pick 1 or 2."
                ;;
        esac
    done
}
# ---------------------------------------------------------------------------
# 1c. AniList route — public list by username, no OAuth/credentials   [NEW]
# ---------------------------------------------------------------------------
ask_anilist_username() {
    read -rp "AniList username: " ANILIST_USERNAME
    if [ -z "$ANILIST_USERNAME" ]; then
        err "No username entered."
        exit 1
    fi
}
fetch_anilist_list() {
    log "Fetching $ANILIST_USERNAME's AniList anime list (no login required)..."
    mkdir -p "$CACHE_DIR"
    proxychains python3 "$SCRIPT_DIR/anilist_fetch_list.py" "$ANILIST_USERNAME"
}
# ---------------------------------------------------------------------------
# 2. Launch callback.py and oauth.py in their own terminals
# ---------------------------------------------------------------------------
start_callback_server() {
    log "Starting callback.py in a new terminal..."
    spawn_terminal "eww-animelist: callback" "python3 callback.py"
}
start_oauth_flow() {
    log "Starting oauth.py in a new terminal (this opens your browser to log in)..."
    spawn_terminal "eww-animelist: oauth" "python3 oauth.py"
}
# ---------------------------------------------------------------------------
# 3. Wait for cache/code.txt to be written with content
# ---------------------------------------------------------------------------
wait_for_code() {
    log "Waiting for MyAnimeList auth code (complete the login in your browser)..."
    mkdir -p "$CACHE_DIR"
    local waited=0
    local timeout=300  # 5 minutes
    while [ ! -s "$CODE_FILE" ]; do
        sleep 1
        waited=$((waited + 1))
        if [ "$waited" -ge "$timeout" ]; then
            err "Timed out waiting for $CODE_FILE. Aborting."
            exit 1
        fi
    done
    log "Auth code received."
}
# ---------------------------------------------------------------------------
# 4. Get token, update widget, open eww
# ---------------------------------------------------------------------------
get_token() {
    log "Running get_token.py..."
    # get_token.py reads cache/code.txt directly — no stdin redirect needed
    proxychains python3 "$SCRIPT_DIR/get_token.py"
}
update_widget() {
    log "Running update_widget.py..."
    if [ "$SOURCE" = "anilist" ]; then
        proxychains python3 "$SCRIPT_DIR/update_widget.py" --source anilist --username "$ANILIST_USERNAME"
    else
        proxychains python3 "$SCRIPT_DIR/update_widget.py" --source mal
    fi
}
open_widget() {
    log "Opening eww widget: $ANIME_WIDGET"
    eww open "$ANIME_WIDGET"
}
# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    cd "$SCRIPT_DIR"
    detect_terminal
    choose_theme
    apply_theme
    choose_source
    if [ "$SOURCE" = "anilist" ]; then
        ask_anilist_username
        fetch_anilist_list
    else
        setup_credentials
        start_callback_server
        sleep 1   # give the flask server a moment to bind before oauth opens the browser
        start_oauth_flow
        wait_for_code
        get_token
    fi
    update_widget
    open_widget
    log "Done."
}
main "$@"
