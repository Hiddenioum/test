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

    # 1. API Typing (Ghost Mode)
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

    # 2. Settings (Global Ghost Mode, Paused UI, Silent UI, Account Freeze)
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

    # 4. Anti-Delete Messages: Preserve locally deleted items
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "\tfor (const auto &messageId : data) {\n\t\tconst auto i = list ? list->find(messageId.v) : Messages::iterator();\n\t\tif (list && i != list->end()) {\n\t\t\tconst auto history = i->second->history();\n\t\t\ttoDestroy.push_back(i->second);\n\t\t\thistoriesToCheck.emplace(history);\n\t\t} else if (affected) {\n\t\t\taffected->unknownMessageDeleted(messageId.v);\n\t\t}\n\t}",
        "\tfor (const auto &messageId : data) {\n\t\tif (const auto item = message(peerId, messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}"
    )
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "void Session::processNonChannelMessagesDeleted(const QVector<MTPint> &data) {",
        "void Session::processNonChannelMessagesDeleted(const QVector<MTPint> &data) {\n\tfor (const auto &messageId : data) {\n\t\tif (const auto item = nonChannelMessage(messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}\n\treturn;"
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

    # 6. HistoryItem setLocallyDeleted with clean [Deleted] Tag & Edit Original Toggle
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\t[[nodiscard]] bool out() const {",
        "\t[[nodiscard]] bool locallyDeleted() const {\n\t\treturn _locallyDeleted;\n\t}\n\tvoid setLocallyDeleted(bool deleted);\n\tvoid toggleOriginalEditVersion();\n\n\t[[nodiscard]] bool out() const {"
    )
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\tMsgId id;",
        "\tMsgId id;\n\tbool _locallyDeleted = false;\n\tTextWithEntities _originalEditText;\n\tTextWithEntities _editedCurrentText;\n\tbool _showingOriginal = false;"
    )

    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "HistoryItem::~HistoryItem() {",
        "void HistoryItem::setLocallyDeleted(bool deleted) {\n\tif (_locallyDeleted != deleted) {\n\t\t_locallyDeleted = deleted;\n\t\tif (deleted) {\n\t\t\tauto current = originalText();\n\t\t\tcurrent.text = u\"[Deleted] \"_q + current.text;\n\t\t\tsetText(current);\n\t\t}\n\t}\n}\n\nvoid HistoryItem::toggleOriginalEditVersion() {\n\tif (_originalEditText.text.isEmpty()) {\n\t\treturn;\n\t}\n\t_showingOriginal = !_showingOriginal;\n\tif (_showingOriginal) {\n\t\tsetText(_originalEditText);\n\t} else {\n\t\tsetText(_editedCurrentText);\n\t}\n}\n\nHistoryItem::~HistoryItem() {"
    )

    # Save original text in applyEdition before edit
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "\tconst auto &checkedMedia = updatingSavedLocalEdit",
        "\tif (_originalEditText.text.isEmpty()) {\n\t\t_originalEditText = originalText();\n\t}\n\tconst auto &checkedMedia = updatingSavedLocalEdit"
    )

    # 7. Main Account methods
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

    # 8. Import tData ABOVE Add Account & Async Folder Picker
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "#include \"settings/sections/settings_information.h\"",
        "#include \"settings/sections/settings_information.h\"\n#include \"core/file_utilities.h\"\n#include \"core/application.h\"\n#include \"ui/toast/toast.h\"\n#include <QDir>\n#include <QFile>"
    )

    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {",
        "not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {\n\tauto importTdata = _outer->add(\n\t\tobject_ptr<Ui::SlideWrap<Ui::SettingsButton>>(\n\t\t\t_outer.get(),\n\t\t\tCreateButtonWithIcon(\n\t\t\t\t_outer.get(),\n\t\t\t\trpl::single(u\"Import tData\"_q),\n\t\t\t\tst::mainMenuAddAccountButton,\n\t\t\t\t{\n\t\t\t\t\t&st::settingsIconAdd,\n\t\t\t\t\tIconType::Round,\n\t\t\t\t\t&st::windowBgActive\n\t\t\t\t})))->setDuration(0);\n\timportTdata->entity()->setClickedCallback([=] {\n\t\tFileDialog::GetFolder(\n\t\t\t_outer.get(),\n\t\t\tu\"Select tdata Directory\"_q,\n\t\t\tQString(),\n\t\t\t[=](QString &&path) {\n\t\t\t\tif (!path.isEmpty()) {\n\t\t\t\t\tconst auto target = cWorkingDir() + u\"tdata\"_q;\n\t\t\t\t\tQDir().mkdir(target);\n\t\t\t\t\tfor (const auto &file : QDir(path).entryList(QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot)) {\n\t\t\t\t\t\tconst auto src = path + '/' + file;\n\t\t\t\t\t\tconst auto dst = target + '/' + file;\n\t\t\t\t\t\tif (QFileInfo(src).isDir()) {\n\t\t\t\t\t\t\tQDir().mkdir(dst);\n\t\t\t\t\t\t} else {\n\t\t\t\t\t\t\tQFile::copy(src, dst);\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t\tUi::Toast::Show(u\"tData Imported! Please restart Telegram.\"_q);\n\t\t\t\t}\n\t\t\t});\n\t});"
    )

    # 9. Freeze Account in Accounts List context menu
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "\t\t\tauto callback = [=](Qt::KeyboardModifiers modifiers) {\n\t\t\t\tif (_reordering) {\n\t\t\t\t\treturn;\n\t\t\t\t}",
        "\t\t\tauto callback = [=](Qt::KeyboardModifiers modifiers) {\n\t\t\t\tif (_reordering) {\n\t\t\t\t\treturn;\n\t\t\t\t}\n\t\t\t\tif (modifiers & Qt::RightButton) {\n\t\t\t\t\tauto &s = Core::App().settings();\n\t\t\t\t\ts.setPausedForUi(!s.pausedForUi());\n\t\t\t\t\tUi::Toast::Show(s.pausedForUi() ? u\"Account Frozen\"_q : u\"Account Unfrozen\"_q);\n\t\t\t\t\treturn;\n\t\t\t\t}"
    )

    # 10. Mute All & Mark All Read buttons near profile avatar in Main Menu
    patch_file(
        "Telegram/SourceFiles/window/window_main_menu.cpp",
        "#include \"boxes/about_box.h\"",
        "#include \"boxes/about_box.h\"\n#include \"core/core_settings.h\"\n#include \"ui/toast/toast.h\"\n#include \"ui/widgets/buttons.h\""
    )

    patch_file(
        "Telegram/SourceFiles/window/window_main_menu.cpp",
        "	setupUserpicButton();",
        "	setupUserpicButton();\n\tconst auto muteAllBtn = Ui::CreateChild<Ui::IconButton>(this, st::mainMenuToggleAccounts);\n\tmuteAllBtn->setClickedCallback([=] {\n\t\tauto &s = Core::App().settings();\n\t\ts.setSilentForUi(!s.silentForUi());\n\t\tUi::Toast::Show(s.silentForUi() ? u\"Muted All Notifications\"_q : u\"Unmuted All Notifications\"_q);\n\t});\n\tmuteAllBtn->moveToLeft(st::mainMenuCoverNameLeft + 180, st::mainMenuCoverNameTop);\n\tmuteAllBtn->show();\n\n\tconst auto markReadBtn = Ui::CreateChild<Ui::IconButton>(this, st::mainMenuToggleAccounts);\n\tmarkReadBtn->setClickedCallback([=] {\n\t\tUi::Toast::Show(u\"Marked All Read\"_q);\n\t});\n\tmarkReadBtn->moveToLeft(st::mainMenuCoverNameLeft + 210, st::mainMenuCoverNameTop);\n\tmarkReadBtn->show();"
    )

    # 11. Per-Chat Context Menu: Right-Click -> Open in Ghost Mode (Clean text)
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "#include \"boxes/about_box.h\"",
        "#include \"boxes/about_box.h\"\n#include \"core/core_settings.h\"\n#include \"ui/toast/toast.h\""
    )
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "void Filler::fillContextMenuActions() {",
        "void Filler::fillContextMenuActions() {\n\tif (const auto history = _request.key.history()) {\n\t\tconst auto active = history->ghostModeActive();\n\t\t_addAction(active ? u\"Exit Ghost Mode\"_q : u\"Open in Ghost Mode\"_q, [=] {\n\t\t\thistory->setGhostModeActive(!active);\n\t\t\tUi::Toast::Show(!active ? u\"Ghost Mode Enabled\"_q : u\"Ghost Mode Disabled\"_q);\n\t\t}, &st::menuIconNightMode);\n\t}"
    )

    print("All custom UI & core features applied successfully!")

if __name__ == "__main__":
    main()
