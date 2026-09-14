#!/usr/bin/env bash
#
# Interactive downloader for The Rosario Dataset v2.
# Source: http://fs01.cifasis-conicet.gov.ar:90/~robot_desmalezador/rosariov2/
# Website: https://cifasis.github.io/rosariov2/
#
# Run with no arguments for an interactive checklist-driven session, or pass
# flags to script/automate it. Run with --help for the full option list.

set -uo pipefail

BASE_URL="http://fs01.cifasis-conicet.gov.ar:90/~robot_desmalezador/rosariov2/sequences"
DEFAULT_DEST="./rosbags"
SAFETY_MARGIN_BYTES=$((2 * 1024 * 1024 * 1024)) # keep 2 GiB free beyond each file's own size

SEQ_IDS=(
    "2023-12-22-13-14-16"
    "2023-12-22-14-29-43"
    "2023-12-22-16-31-08"
    "2023-12-26-13-39-43"
    "2023-12-26-15-10-15"
    "2023-12-26-15-48-38"
)
SEQ_LABELS=(
    "#1  2023-12-22-13-14-16  (940s,  777m)"
    "#2  2023-12-22-14-29-43  (1011s, 904m)"
    "#3  2023-12-22-16-31-08  (943s,  950m)"
    "#4  2023-12-26-13-39-43  (2506s, 2254m)"
    "#5  2023-12-26-15-10-15  (796s,  703m)"
    "#6  2023-12-26-15-48-38  (1862s, 1744m)"
)

TYPE_KEYS=(base conventional_gnss pgt ppk_gnss odom_fix)
TYPE_LABELS=(
    "Base Rosbag (compressed)               [~29-92 GB each]"
    "Conventional GPS          (Add-On)      [~3-11 MB each]"
    "Pose Ground-Truth         (Add-On)      [~3-28 GB each]"
    "Post-Processed Kinematic GNSS (Add-On)  [~3-11 MB each]"
    "Odometry Fix              (Add-On)      [~6-18 MB each]"
)
declare -A TYPE_SUFFIX=(
    [conventional_gnss]="conventional_gnss.bag"
    [pgt]="pgt.bag"
    [ppk_gnss]="ppk_gnss.bag"
    [odom_fix]="odom_fix.bag"
)

DEST_DIR=""
JOBS=""
ASSUME_YES=0
SEQ_ARG=""
TYPES_ARG=""

print_help() {
    cat <<EOF
Usage: $(basename "$0") [options]

Downloads sequences from The Rosario Dataset v2. With no options this runs a
fully interactive session (checklists for sequences and file types, then
prompts for destination and download mode). Any of the choices below can be
supplied upfront to skip that particular prompt.

Options:
  --dest DIR         Destination directory (default: ${DEFAULT_DEST})
  --sequences LIST   Comma-separated sequence numbers (1-${#SEQ_IDS[@]}), sequence
                      IDs (e.g. 2023-12-22-13-14-16), or "all". Skips the
                      sequence checklist.
  --types LIST       Comma-separated types (${TYPE_KEYS[*]}) or "all".
                      Skips the file type checklist.
  --jobs N           Number of parallel downloads (default: 1, sequential)
  -y, --yes          Assume "yes" on prompts (needed for a fully
                      non-interactive run together with --sequences and
                      --types)
  --list             List available sequences and file types, then exit
  -h, --help         Show this help

Examples:
  # Fully interactive
  $(basename "$0")

  # Only base rosbags for sequences 1 and 4, into /data/rosbags, 3 in parallel
  $(basename "$0") --sequences 1,4 --types base --dest /data/rosbags --jobs 3 -y

  # Everything, sequentially
  $(basename "$0") --sequences all --types all -y
EOF
}

list_available() {
    echo "Sequences:"
    local i
    for i in "${!SEQ_IDS[@]}"; do
        printf "  %d) %s\n" "$((i + 1))" "${SEQ_LABELS[$i]}"
    done
    echo
    echo "File types:"
    for i in "${!TYPE_KEYS[@]}"; do
        printf "  %-18s %s\n" "${TYPE_KEYS[$i]}" "${TYPE_LABELS[$i]}"
    done
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dest)
                DEST_DIR=$2
                shift 2
                ;;
            --sequences)
                SEQ_ARG=$2
                shift 2
                ;;
            --types)
                TYPES_ARG=$2
                shift 2
                ;;
            --jobs)
                JOBS=$2
                shift 2
                ;;
            -y | --yes)
                ASSUME_YES=1
                shift
                ;;
            --list)
                list_available
                exit 0
                ;;
            -h | --help)
                print_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                print_help
                exit 1
                ;;
        esac
    done
}

filename_for() {
    local seq=$1 type=$2
    if [[ "$type" == "base" ]]; then
        echo "${seq}.compressed.bag"
    else
        echo "${seq}_${TYPE_SUFFIX[$type]}"
    fi
}

human_size() {
    local bytes=${1:-0}
    numfmt --to=iec --suffix=B "$bytes" 2>/dev/null || echo "${bytes} bytes"
}

get_remote_size() {
    local url=$1 size
    size=$(curl -sI "$url" 2>/dev/null | tr -d '\r' | grep -i '^content-length:' | tail -1 | awk '{print $2}')
    echo "${size:-0}"
}

get_free_bytes() {
    df -B1 --output=avail "$1" 2>/dev/null | tail -1 | tr -d ' '
}

# checklist_select TITLE LABELS_ARRAY_NAME SELECTED_ARRAY_NAME
checklist_select() {
    local title=$1
    local -n _labels=$2
    local -n _sel=$3
    local n=${#_labels[@]}
    local input idx any v

    while true; do
        clear
        echo "=== ${title} ==="
        echo "Enter a number to toggle, 'a' = select all, 'n' = select none, Enter = confirm"
        echo
        for ((idx = 0; idx < n; idx++)); do
            local mark=" "
            [[ "${_sel[$idx]}" == "1" ]] && mark="x"
            printf "  [%s] %2d) %s\n" "$mark" "$((idx + 1))" "${_labels[$idx]}"
        done
        echo
        read -rp "> " input
        case "$input" in
            "")
                any=0
                for v in "${_sel[@]}"; do [[ "$v" == "1" ]] && any=1; done
                if [[ $any -eq 0 ]]; then
                    echo "Select at least one item."
                    read -rp "Press Enter to continue..." _
                    continue
                fi
                break
                ;;
            a | A)
                for ((idx = 0; idx < n; idx++)); do _sel[$idx]=1; done
                ;;
            n | N)
                for ((idx = 0; idx < n; idx++)); do _sel[$idx]=0; done
                ;;
            *)
                if [[ "$input" =~ ^[0-9]+$ ]] && ((input >= 1 && input <= n)); then
                    idx=$((input - 1))
                    if [[ "${_sel[$idx]}" == "1" ]]; then
                        _sel[$idx]=0
                    else
                        _sel[$idx]=1
                    fi
                fi
                ;;
        esac
    done
}

# parse_selection INPUT IDS_ARRAY_NAME SEL_ARRAY_NAME
parse_selection() {
    local input=$1
    local -n ids=$2
    local -n sel=$3
    local n=${#ids[@]}
    local i tok found

    if [[ "$input" == "all" ]]; then
        for ((i = 0; i < n; i++)); do sel[$i]=1; done
        return 0
    fi

    IFS=',' read -ra tokens <<<"$input"
    for tok in "${tokens[@]}"; do
        tok=$(echo "$tok" | xargs)
        found=0
        for ((i = 0; i < n; i++)); do
            if [[ "${ids[$i]}" == "$tok" ]]; then
                sel[$i]=1
                found=1
                break
            fi
        done
        if [[ $found -eq 0 && "$tok" =~ ^[0-9]+$ ]] && ((tok >= 1 && tok <= n)); then
            sel[$((tok - 1))]=1
            found=1
        fi
        [[ $found -eq 0 ]] && echo "Warning: unknown selection '$tok', ignoring." >&2
    done
}

# download_one SEQ TYPE DEST IDX TOTAL PARALLEL
download_one() {
    local seq=$1 type=$2 dest=$3 idx=$4 total=$5 parallel=$6
    local fname url local_path remote_size local_size free_bytes needed reply

    fname=$(filename_for "$seq" "$type")
    url="${BASE_URL}/${fname}"
    local_path="${dest}/${fname}"

    echo "[$idx/$total] ${fname}"

    remote_size=$(get_remote_size "$url")
    local_size=0
    [[ -f "$local_path" ]] && local_size=$(stat -c%s "$local_path" 2>/dev/null || echo 0)

    if [[ "$remote_size" != "0" && "$local_size" == "$remote_size" ]]; then
        echo "    already downloaded, skipping."
        return 0
    fi

    if [[ "$remote_size" != "0" ]]; then
        free_bytes=$(get_free_bytes "$dest")
        needed=$((remote_size - local_size + SAFETY_MARGIN_BYTES))
        if ((free_bytes < needed)); then
            echo "    WARNING: ${fname} needs ~$(human_size "$remote_size"), only $(human_size "$free_bytes") free at ${dest}."
            if [[ "$ASSUME_YES" == "1" || "$parallel" == "1" ]]; then
                echo "    Skipping (insufficient space)."
                return 1
            fi
            read -rp "    Continue downloading anyway? [y/N] " reply
            if [[ ! "$reply" =~ ^[Yy]$ ]]; then
                echo "    Skipped."
                return 1
            fi
        fi
    fi

    local -a curl_opts=(-C - --retry 3 --retry-delay 5 -o "$local_path" "$url")
    if [[ "$parallel" == "1" ]]; then
        curl_opts=(-s "${curl_opts[@]}")
    else
        curl_opts=(--progress-bar "${curl_opts[@]}")
    fi

    if curl "${curl_opts[@]}"; then
        local final_size
        final_size=$(stat -c%s "$local_path" 2>/dev/null || echo 0)
        if [[ "$remote_size" != "0" && "$final_size" != "$remote_size" ]]; then
            echo "    WARNING: size mismatch for ${fname} (expected $(human_size "$remote_size"), got $(human_size "$final_size"))."
        else
            echo "    done ($(human_size "$final_size"))."
        fi
    else
        echo "    ERROR downloading ${fname}"
        return 1
    fi

    free_bytes=$(get_free_bytes "$dest")
    echo "    free space remaining at ${dest}: $(human_size "$free_bytes")"
}

main() {
    parse_args "$@"

    command -v curl >/dev/null || {
        echo "curl is required but was not found." >&2
        exit 1
    }

    echo "Rosario Dataset v2 downloader"
    echo "Server: ${BASE_URL}"
    echo

    local -a SEQ_SEL TYPE_SEL
    local i
    for ((i = 0; i < ${#SEQ_IDS[@]}; i++)); do SEQ_SEL[$i]=1; done
    for ((i = 0; i < ${#TYPE_KEYS[@]}; i++)); do TYPE_SEL[$i]=1; done

    if [[ -n "$SEQ_ARG" ]]; then
        for ((i = 0; i < ${#SEQ_IDS[@]}; i++)); do SEQ_SEL[$i]=0; done
        parse_selection "$SEQ_ARG" SEQ_IDS SEQ_SEL
    else
        checklist_select "Select sequences to download" SEQ_LABELS SEQ_SEL
    fi

    if [[ -n "$TYPES_ARG" ]]; then
        for ((i = 0; i < ${#TYPE_KEYS[@]}; i++)); do TYPE_SEL[$i]=0; done
        parse_selection "$TYPES_ARG" TYPE_KEYS TYPE_SEL
    else
        checklist_select "Select file types to download" TYPE_LABELS TYPE_SEL
    fi

    if [[ -z "$DEST_DIR" ]]; then
        clear
        read -rp "Destination folder [${DEFAULT_DEST}]: " DEST_DIR
        DEST_DIR=${DEST_DIR:-$DEFAULT_DEST}
    fi
    mkdir -p "$DEST_DIR" || {
        echo "Cannot create destination directory: ${DEST_DIR}" >&2
        exit 1
    }

    if [[ -z "$JOBS" ]]; then
        read -rp "Sequential or parallel downloads? [s]equential/[p]arallel (default: sequential): " mode
        if [[ "$mode" =~ ^[Pp] ]]; then
            read -rp "Number of parallel downloads [3]: " JOBS
            JOBS=${JOBS:-3}
        else
            JOBS=1
        fi
    fi

    local -a queue=()
    local j
    for ((i = 0; i < ${#SEQ_IDS[@]}; i++)); do
        [[ "${SEQ_SEL[$i]}" == "1" ]] || continue
        for ((j = 0; j < ${#TYPE_KEYS[@]}; j++)); do
            [[ "${TYPE_SEL[$j]}" == "1" ]] || continue
            queue+=("${SEQ_IDS[$i]}|${TYPE_KEYS[$j]}")
        done
    done

    if [[ ${#queue[@]} -eq 0 ]]; then
        echo "Nothing selected, exiting."
        exit 0
    fi

    echo
    echo "Fetching remote file sizes..."
    local total_bytes=0 item seq type fname sz
    for item in "${queue[@]}"; do
        IFS='|' read -r seq type <<<"$item"
        fname=$(filename_for "$seq" "$type")
        sz=$(get_remote_size "${BASE_URL}/${fname}")
        total_bytes=$((total_bytes + sz))
        printf "  %-45s %10s\n" "$fname" "$(human_size "$sz")"
    done

    echo
    echo "Total: ${#queue[@]} files, $(human_size "$total_bytes")"
    local free_bytes
    free_bytes=$(get_free_bytes "$DEST_DIR")
    echo "Free space at ${DEST_DIR}: $(human_size "$free_bytes")"
    if ((free_bytes < total_bytes)); then
        echo "WARNING: the total selected download size exceeds the currently available free space."
        echo "         Individual files will still be checked against free space as they download."
    fi
    echo

    if [[ "$ASSUME_YES" != "1" ]]; then
        read -rp "Proceed with download? [Y/n] " confirm
        [[ "$confirm" =~ ^[Nn] ]] && {
            echo "Aborted."
            exit 0
        }
    fi

    local idx=0 total=${#queue[@]}
    if ((JOBS <= 1)); then
        for item in "${queue[@]}"; do
            idx=$((idx + 1))
            IFS='|' read -r seq type <<<"$item"
            download_one "$seq" "$type" "$DEST_DIR" "$idx" "$total" 0
        done
    else
        echo "Downloading with up to ${JOBS} parallel jobs..."
        for item in "${queue[@]}"; do
            idx=$((idx + 1))
            while (($(jobs -rp | wc -l) >= JOBS)); do
                wait -n
            done
            IFS='|' read -r seq type <<<"$item"
            (download_one "$seq" "$type" "$DEST_DIR" "$idx" "$total" 1) &
        done
        wait
    fi

    echo
    echo "Done. Files saved under: ${DEST_DIR}"
}

main "$@"
