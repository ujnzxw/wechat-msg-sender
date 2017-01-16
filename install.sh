#!/bin/sh

PKG="wechat-msg-sender"
GIT_URL="https://github.com/ujnzxw/wechat-msg-sender.git"
INSTALL_DIR="${INSTALL_DIR}"

has()
{
    type "$1" > /dev/null 2>&1
}
confirm()
{
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure (default NO)? [y/N]} " response
    case $response in
        [yY][eE][sS]|[yY])
            true
            ;;
        *)
            false
            ;;
    esac
}

install_echo()
{
    echo "[Install] $@"
}

install_from_git()
{
    [ -z "${INSTALL_DIR}" ] && INSTALL_DIR="/usr/local/${PKG}"
    if [ -e "${INSTALL_DIR}" ]; then
        install_echo "${PKG} is already installed"
        install_echo "Updating ${PKG} from git"
        command git --git-dir="${INSTALL_DIR}/.git" --work-tree="${INSTALL_DIR}" fetch --depth=1 ||
        {
            install_echo >&2 "Failed to fetch changes => ${GIT_URL}"
            exit 1
        }
        command git --git-dir="${INSTALL_DIR}/.git" --work-tree="${INSTALL_DIR}" reset --hard origin/master ||
        {
            install_echo >&2 "Failed to reset changes => ${GIT_URL}"
            exit 1
        }
    else
        install_echo "Downloading ${PKG} from git to ${INSTALL_DIR}"
        command git clone --depth 1 ${GIT_URL} ${INSTALL_DIR} ||
        {
            install_echo >&2 "Failed to clone => ${GIT_URL}"
            exit 1
        }
        chmod -R 755 ${INSTALL_DIR}/lib  2>/dev/null
        chmod -R 755 ${INSTALL_DIR}/wechat.py 2>/dev/null
        chmod 755 ${INSTALL_DIR}/sender 2>/dev/null
        sudo ln -sf ${INSTALL_DIR}/sender /usr/local/bin/wechat-msg-sender
    fi
}

# Check if /bin/sh is linked to /bin/bash
command ls -l /bin/sh | grep bash > /dev/null 2>&1 ||
{
    install_echo >&2 "/bin/sh is not linked to /bin/bash"
    install_echo >&2 "Please use ln to link it first!"
    exit 1
}

if has "git"; then
    install_from_git;
else
    install_echo >&2 "Failed to install, please install git before."
fi

[ -z "${INSTALL_DIR}" ] && INSTALL_DIR="/usr/local/${PKG}"

if [ -f "${INSTALL_DIR}/u" ]; then
    install_echo ""
    install_echo "Done!"
else
    install_echo >&2 ""
    install_echo >&2 "Something went wrong. ${INSTALL_DIR}/u not found"
    install_echo >&2 ""
    exit 1
fi

