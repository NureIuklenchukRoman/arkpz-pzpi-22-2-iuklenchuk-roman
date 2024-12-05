#!/bin/bash

function show_commands() {
    echo "Available COMMANDS: "
    echo "start"
    echo "build"
    echo "db"
}

# Start command
function start() {
    docker-compose up -d
    docker image prune --force
}

# Build command
function build () {
    docker-compose build
}

# Database command
function db() {
    cd ./backend || exit
    # Downgrade function
    function downgrade() {
        alembic -x data=true downgrade -1
    }

    # Update head function
    function update_head() {
        alembic upgrade head
    }

    # Commit function
    function commit() {
        comment=$(printf "%s_" "${@}")
        alembic revision --autogenerate -m "$comment"
    }

    # Available commands for db
    COMMANDS=("downgrade" "update_head" "commit")

    if [[ $# -gt 0 ]]; then
        if [[ " ${COMMANDS[@]} " =~ " $1 " ]]; then
            # Dynamically call the function
            $1 "${@:2}"
        else
            echo "Invalid command. Available commands for db: ${COMMANDS[@]}"
        fi
    else
        # Show available db commands in the desired format
        echo "Available DB commands: "
        for cmd in "${COMMANDS[@]}"; do
            printf "%-15s\n" "$cmd"
        done
    fi
}

# Main command dispatch
if [[ $# -gt 0 ]]; then
    case "$1" in
        "start")
            start
            ;;
        "build")
            build
            ;;
        "db")
            db "${@:2}"
            ;;
        *)
            show_commands
            ;;
    esac
else
    show_commands
fi
