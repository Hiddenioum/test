#!/usr/bin/env python3
import os
import sys

def patch_file(filepath, target, replacement):
    if not os.path.exists(filepath):
        print(f"Skipping missing file: {filepath}")
        return
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if target not in content:
        raise RuntimeError(f"Target string not found in {filepath}: {repr(target[:50])}")
    content = content.replace(target, replacement, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {filepath} successfully.")

def main():
    print("Applying custom features for Telegram Desktop v7.0.5...")

    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "\tconst auto requestId = _session->api().request(MTPmessages_SetTyping(",
        "\tif (key.history && key.history->ghostModeActive()) {\n\t\treturn;\n\t}\n\tconst auto requestId = _session->api().request(MTPmessages_SetTyping("
    )

    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}\n\tvoid setPausedForUi(bool paused) { _pausedForUi = paused; }\n\t[[nodiscard]] bool pausedForUi() const { return _pausedForUi; }\n\tvoid setSilentForUi(bool silent) { _silentForUi = silent; }\n\t[[nodiscard]] bool silentForUi() const { return _silentForUi; }"
    )

    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tbool _loopAnimatedStickers = true;",
        "\tbool _loopAnimatedStickers = true;\n\tbool _pausedForUi = false;\n\tbool _silentForUi = false;"
    )

    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {\n\tif (history->ghostModeActive()) {\n\t\tstate.willReadTill = 0;\n\t\tstate.willReadWhen = 0;\n\t\treturn;\n\t}"
    )

    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "\tauto toDestroy = std::vector<not_null<HistoryItem*>>();\n\tauto historiesToCheck = base::flat_set<not_null<History*>>();",
        "\tfor (const auto &messageId : data) {\n\t\tif (const auto item = message(peerId, messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}\n\tauto toDestroy = std::vector<not_null<HistoryItem*>>();\n\tauto historiesToCheck = base::flat_set<not_null<History*>>();"
    )

    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "History::~History() = default;",
        "History::~History() = default;\n\nvoid History::setGhostModeActive(bool active) {\n\t_ghostModeActive = active;\n}\n\nbool History::ghostModeActive() const {\n\treturn _ghostModeActive;\n}"
    )

    patch_file(
        "Telegram/SourceFiles/history/history.h",
        "\tData::Folder *folder() const override;",
        "\tData::Folder *folder() const override;\n\n\tvoid setGhostModeActive(bool active);\n\t[[nodiscard]] bool ghostModeActive() const;"
    )

    patch_file(
        "Telegram/SourceFiles/history/history.h",
        "\tstd::optional<Data::Folder*> _folder;",
        "\tstd::optional<Data::Folder*> _folder;\n\tbool _ghostModeActive = false;"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\t[[nodiscard]] bool out() const {",
        "\t[[nodiscard]] bool locallyDeleted() const {\n\t\treturn _locallyDeleted;\n\t}\n\tvoid setLocallyDeleted(bool deleted) {\n\t\t_locallyDeleted = deleted;\n\t}\n\n\t[[nodiscard]] bool out() const {"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\tMsgId id;",
        "\tMsgId id;\n\tbool _locallyDeleted = false;"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item_components.h",
        "struct HistoryMessageEdited",
        "struct HistoryMessageEditRevisions {\n\tstd::vector<int> list;\n};\n\nstruct HistoryMessageEdited"
    )

    patch_file(
        "Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp",
        "void TopBarWidget::paintTopBar(Painter &p) {",
        "void TopBarWidget::paintTopBar(Painter &p) {\n\tif (const auto history = _activeChat.key.owningHistory()) {\n\t\tif (history->ghostModeActive()) {\n\t\t\tp.setFont(st::dialogsTextFont);\n\t\t\tp.setPen(st::dialogsNameFg);\n\t\t\tp.drawText(width() - _rightTaken - 80, st::topBarArrowPadding.top(), u\"Ghost\"_q);\n\t\t}\n\t}"
    )

    patch_file(
        "Telegram/SourceFiles/main/main_account.cpp",
        "void Account::logOut() {",
        "void Account::setPausedForUi(bool paused) {\n\tCore::App().settings().setPausedForUi(paused);\n}\n\nbool Account::pausedForUi() const {\n\treturn Core::App().settings().pausedForUi();\n}\n\nvoid Account::setSilentForUi(bool silent) {\n\tCore::App().settings().setSilentForUi(silent);\n}\n\nbool Account::silentForUi() const {\n\treturn Core::App().settings().silentForUi();\n}\n\nvoid Account::logOut() {"
    )

    patch_file(
        "Telegram/SourceFiles/main/main_account.h",
        "\tvoid logOut();",
        "\tvoid logOut();\n\tvoid setPausedForUi(bool paused);\n\t[[nodiscard]] bool pausedForUi() const;\n\tvoid setSilentForUi(bool silent);\n\t[[nodiscard]] bool silentForUi() const;"
    )

    patch_file(
        "Telegram/SourceFiles/main/main_domain.cpp",
        "void Domain::activate(not_null<Main::Account*> account) {",
        "void Domain::setAccountPaused(not_null<Account*> account, bool paused) {\n\taccount->setPausedForUi(paused);\n}\n\nvoid Domain::setAccountSilent(not_null<Account*> account, bool silent) {\n\taccount->setSilentForUi(silent);\n}\n\nvoid Domain::activate(not_null<Main::Account*> account) {"
    )

    patch_file(
        "Telegram/SourceFiles/main/main_domain.h",
        "\tvoid activate(not_null<Main::Account*> account);",
        "\tvoid activate(not_null<Main::Account*> account);\n\tvoid setAccountPaused(not_null<Account*> account, bool paused);\n\tvoid setAccountSilent(not_null<Account*> account, bool silent);"
    )

    print("All custom features applied successfully!")

if __name__ == "__main__":
    main()
