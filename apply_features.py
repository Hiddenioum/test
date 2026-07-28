#!/usr/bin/env python3
import os
import sys

def patch_file(filepath, target, replacement):
    if not os.path.exists(filepath):
        print(f"Skipping missing file: {filepath}")
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if target not in content:
        raise RuntimeError(f"Target string not found in {filepath}: {repr(target[:50])}")
    content = content.replace(target, replacement, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {filepath} successfully.")
    return True

def main():
    print("Applying custom features for Telegram Desktop v7.0.5...")

    # 1. API Typing (Ghost Mode) - add missing include first
    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "#include \"api/api_send_progress.h\"",
        "#include \"api/api_send_progress.h\"\n#include \"core/application.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "\tconst auto requestId = _session->api().request(MTPmessages_SetTyping(",
        "\tif ((key.history && key.history->ghostModeActive()) || Core::App().settings().globalGhostMode()) {\n\t\treturn;\n\t}\n\tconst auto requestId = _session->api().request(MTPmessages_SetTyping("
    )

    # 2. Settings (Global Ghost Mode, Paused UI, Silent UI)
    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}\n\tvoid setPausedForUi(bool paused) { _pausedForUi = paused; }\n\t[[nodiscard]] bool pausedForUi() const { return _pausedForUi; }\n\tvoid setSilentForUi(bool silent) { _silentForUi = silent; }\n\t[[nodiscard]] bool silentForUi() const { return _silentForUi; }\n\tvoid setGlobalGhostMode(bool ghost) { _globalGhostMode = ghost; }\n\t[[nodiscard]] bool globalGhostMode() const { return _globalGhostMode; }"
    )

    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tbool _loopAnimatedStickers = true;",
        "\tbool _loopAnimatedStickers = true;\n\tbool _pausedForUi = false;\n\tbool _silentForUi = false;\n\tbool _globalGhostMode = false;"
    )

    # 3. Read Requests (Ghost Mode)
    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "#include \"core/application.h\"",
        "#include \"core/application.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {\n\tif (history->ghostModeActive() || Core::App().settings().globalGhostMode()) {\n\t\tstate.willReadTill = 0;\n\t\tstate.willReadWhen = 0;\n\t\treturn;\n\t}"
    )

    # 4. Deleted Messages (Keep & Tag [Deleted])
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "\tauto toDestroy = std::vector<not_null<HistoryItem*>>();\n\tauto historiesToCheck = base::flat_set<not_null<History*>>();",
        "\tfor (const auto &messageId : data) {\n\t\tif (const auto item = message(peerId, messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}\n\tauto toDestroy = std::vector<not_null<HistoryItem*>>();\n\tauto historiesToCheck = base::flat_set<not_null<History*>>();"
    )

    # 5. History Ghost Mode Methods
    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "#include \"core/ui_integration.h\"",
        "#include \"core/ui_integration.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "History::~History() = default;",
        "History::~History() = default;\n\nvoid History::setGhostModeActive(bool active) {\n\t_ghostModeActive = active;\n}\n\nbool History::ghostModeActive() const {\n\treturn _ghostModeActive || Core::App().settings().globalGhostMode();\n}"
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

    # 6. HistoryItem setLocallyDeleted with [Deleted] Tag
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\t[[nodiscard]] bool out() const {",
        "\t[[nodiscard]] bool locallyDeleted() const {\n\t\treturn _locallyDeleted;\n\t}\n\tvoid setLocallyDeleted(bool deleted);\n\n\t[[nodiscard]] bool out() const {"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\tMsgId id;",
        "\tMsgId id;\n\tbool _locallyDeleted = false;"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "HistoryItem::~HistoryItem() {",
        "void HistoryItem::setLocallyDeleted(bool deleted) {\n\tif (_locallyDeleted != deleted) {\n\t\t_locallyDeleted = deleted;\n\t\tif (deleted) {\n\t\t\tauto current = originalText();\n\t\t\tcurrent.text = u\"\\U0001F5D1\\U0000FE0F [Deleted] \"_q + current.text;\n\t\t\tsetText(current);\n\t\t}\n\t}\n}\n\nHistoryItem::~HistoryItem() {"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item_components.h",
        "struct HistoryMessageEdited",
        "struct HistoryMessageEditRevisions {\n\tstd::vector<int> list;\n};\n\nstruct HistoryMessageEdited"
    )

    # 7. Top Bar Ghost Mode Badge
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp",
        "void TopBarWidget::paintTopBar(Painter &p) {",
        "void TopBarWidget::paintTopBar(Painter &p) {\n\tif (const auto history = _activeChat.key.owningHistory()) {\n\t\tif (history->ghostModeActive()) {\n\t\t\tp.setFont(st::dialogsTextFont);\n\t\t\tp.setPen(st::dialogsNameFg);\n\t\t\tp.drawText(width() - _rightTaken - 100, st::topBarArrowPadding.top(), u\"\\U0001F47B Ghost\"_q);\n\t\t}\n\t}"
    )

    # 8. Main Account methods
    patch_file(
        "Telegram/SourceFiles/main/main_account.cpp",
        "#include \"core/application.h\"",
        "#include \"core/application.h\"\n#include \"core/core_settings.h\""
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

    # 9. Main Menu: Add Ghost Mode Toggle & Import tdata Button!
    patch_file(
        "Telegram/SourceFiles/window/window_main_menu.cpp",
        "#include \"boxes/about_box.h\"",
        "#include \"boxes/about_box.h\"\n#include \"core/core_settings.h\"\n#include \"ui/toast/toast.h\"\n#include <QFileDialog>\n#include <QDir>\n#include <QFile>"
    )

    patch_file(
        "Telegram/SourceFiles/window/window_main_menu.cpp",
        "\taddAction(\n\t\ttr::lng_menu_settings(),\n\t\t{ &st::menuIconSettings }\n\t)->setClickedCallback([=] {\n\t\tcontroller->showSettings();\n\t});",
        "\taddAction(\n\t\ttr::lng_menu_settings(),\n\t\t{ &st::menuIconSettings }\n\t)->setClickedCallback([=] {\n\t\tcontroller->showSettings();\n\t});\n\n\t_menu->add(\n\t\tCreateButtonWithIcon(\n\t\t\t_menu,\n\t\t\trpl::single(u\"\\U0001F47B Ghost Mode\"_q),\n\t\t\tst::mainMenuButton,\n\t\t\t{ &st::menuIconNightMode })\n\t)->setClickedCallback([=] {\n\t\tauto &s = Core::App().settings();\n\t\ts.setGlobalGhostMode(!s.globalGhostMode());\n\t\tCore::App().saveSettingsDelayed();\n\t\tUi::Toast::Show(s.globalGhostMode() ? u\"\\U0001F47B Ghost Mode ON\"_q : u\"\\U0001F47B Ghost Mode OFF\"_q);\n\t});\n\n\t_menu->add(\n\t\tCreateButtonWithIcon(\n\t\t\t_menu,\n\t\t\trpl::single(u\"\\U0001F4C2 Import tdata\"_q),\n\t\t\tst::mainMenuButton,\n\t\t\t{ &st::menuIconRestore })\n\t)->setClickedCallback([=] {\n\t\tconst auto path = QFileDialog::getExistingDirectory(\n\t\t\tnullptr,\n\t\t\tu\"Select tdata Directory\"_q,\n\t\t\tQString());\n\t\tif (!path.isEmpty()) {\n\t\t\tconst auto target = cWorkingDir() + u\"tdata\"_q;\n\t\t\tQDir().mkdir(target);\n\t\t\tfor (const auto &file : QDir(path).entryList(QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot)) {\n\t\t\t\tconst auto src = path + '/' + file;\n\t\t\t\tconst auto dst = target + '/' + file;\n\t\t\t\tif (QFileInfo(src).isDir()) {\n\t\t\t\t\tQDir().mkdir(dst);\n\t\t\t\t} else {\n\t\t\t\t\tQFile::copy(src, dst);\n\t\t\t\t}\n\t\t\t}\n\t\t\tUi::Toast::Show(u\"tdata Imported! Restarting...\"_q);\n\t\t\tCore::App().restart();\n\t\t}\n\t});"
    )

    # 10. Per-Chat Context Menu: Right-Click -> Toggle Ghost Mode
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "#include \"boxes/about_box.h\"",
        "#include \"boxes/about_box.h\"\n#include \"core/core_settings.h\"\n#include \"ui/toast/toast.h\""
    )

    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "void Filler::fillContextMenuActions() {",
        "void Filler::fillContextMenuActions() {\n\tif (const auto history = _request.key.history()) {\n\t\tconst auto active = history->ghostModeActive();\n\t\t_addAction(active ? u\"\\U0001F47B Disable Ghost Mode\"_q : u\"\\U0001F47B Enable Ghost Mode\"_q, [=] {\n\t\t\thistory->setGhostModeActive(!active);\n\t\t\tUi::Toast::Show(!active ? u\"\\U0001F47B Ghost Mode ON for this chat\"_q : u\"\\U0001F47B Ghost Mode OFF for this chat\"_q);\n\t\t}, &st::menuIconNightMode);\n\t}"
    )

    print("All custom UI & core features applied successfully!")

if __name__ == "__main__":
    main()
